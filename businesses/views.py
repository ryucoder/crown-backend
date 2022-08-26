from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.utils import CurrentPagePagination, CommonUtil

from users.models import EmailUser

from businesses.serializers import (
    BusinessSerializer,
    BusinessAccountSerializer,
    BusinessAddressSerializer,
    BusinessContactSerializer,
    ToggleDefaultBusinessAddressSerializer,
    OrderSerializer,
    UpdateOrderStatusSerializer,
    BusinessWithOwnerSerializer,
)
from businesses.models import (
    Business,
    BusinessAccount,
    # BusinessContact,
    BusinessConnect,
    Order,
)


class BusinessViewset(viewsets.ModelViewSet):

    serializer_class = BusinessSerializer
    pagination_class = CurrentPagePagination
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = (
            EmailUser.objects.filter(id=self.request.user.pk)
            # .select_related("business")
            .first()
        )
        context["action"] = self.action
        return context

    def get_queryset(self):
        queryset = Business.objects.all().prefetch_related(
            "contacts", "addresses", "accounts"
        )
        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "create_business_with_owner":
            serializer = BusinessWithOwnerSerializer

        return serializer

    @action(detail=False, methods=["get"])
    def customers_of_laboratory(self, request, *args, **kwargs):

        current_user = (
            EmailUser.objects.filter(id=request.user.pk)
            .select_related("owned_business")
            .first()
        )

        current_business = current_user.get_business()

        queryset = current_business.connected_businesses.all().order_by("-created_at")

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset=queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def create_business_with_owner(self, request, *args, **kwargs):

        context = self.get_serializer_context()
        serializer = BusinessWithOwnerSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=False, methods=["get"])
    def except_mine(self, request, *args, **kwargs):

        current_user = (
            EmailUser.objects.filter(id=request.user.pk)
            .select_related("owned_business")
            .first()
        )

        current_business = current_user.get_business()

        queryset = Business.objects.exclude(id=current_business.id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OrderViewset(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    pagination_class = CurrentPagePagination
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_permissions(self):

        # dentist users
        # create    - only denstists or his employees can create accounts
        # read      - dentist owner can view all orders, dentist employee can view orders created by him
        # update    - dentist can update all order if they arein certain statuses
        # delete    - dentist users can delete orders that are having status of pending

        # laboratory users
        # create    - cant create orders
        # read      - laboratory owner can view all orders, laboratory employee can view his orders
        # update    - laboratory owner can update the status of all orders,
        #             laboratory employee can update the status of his orders,
        # delete    - laboratory users cant delete any orders

        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = (
            EmailUser.objects.filter(id=self.request.user.pk)
            # .select_related("business")
            .first()
        )
        context["action"] = self.action
        return context

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "update_order_status":
            serializer = UpdateOrderStatusSerializer

        return serializer

    def get_queryset(self):

        user = EmailUser.objects.filter(id=self.request.user.pk).first()
        users_business = user.get_business()

        queryset = (
            Order.objects.filter(
                Q(from_business=users_business) | Q(to_business=users_business)
            )
            .select_related("from_business")
            .order_by("-created_at")
        )

        # TODO: Need to find a way to do this via annotate or do it at the time of creation
        for order in queryset:
            if order.from_business.id == users_business.id:
                order.order_type = "placed"
            else:
                order.order_type = "received"

        return queryset

    @action(detail=True, methods=["put"])
    def update_order_status(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BusinessAccountViewset(viewsets.ModelViewSet):

    serializer_class = BusinessAccountSerializer
    # pagination_class = CurrentPagePagination
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_permissions(self):
        # For add_business_account
        #   only owner can create accounts

        return super().get_permissions()

    def get_queryset(self):
        user = EmailUser.objects.filter(id=self.request.user.pk).first()
        queryset = BusinessAccount.objects.filter(business=user.get_business())
        return queryset

    def perform_create(self, serializer):
        user = EmailUser.objects.filter(id=self.request.user.pk).first()
        serializer.save(user=user)


class BusinessAddressViewset(viewsets.ModelViewSet):

    serializer_class = BusinessAddressSerializer
    # pagination_class = CurrentPagePagination
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_permissions(self):
        # For add, edit and delete business_address
        #   only owner

        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = (
            EmailUser.objects.filter(id=self.request.user.pk)
            .select_related("business")
            .prefetch_related("business__addresses")
            .first()
        )
        return context

    def get_queryset(self):
        user = (
            EmailUser.objects.filter(id=self.request.user.pk)
            .select_related("business")
            .prefetch_related("business__addresses")
            .first()
        )
        queryset = user.business.addresses.all()
        return queryset

    @action(detail=True, methods=["put"])
    def toggle_is_default(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = ToggleDefaultBusinessAddressSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        serializer = BusinessAddressSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BusinessContactViewset(viewsets.ModelViewSet):

    serializer_class = BusinessContactSerializer
    # pagination_class = CurrentPagePagination
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_permissions(self):
        # For add, edit and delete business_address
        #   only owner

        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = (
            EmailUser.objects.filter(id=self.request.user.pk)
            .select_related("business")
            .prefetch_related("business__contacts")
            .first()
        )
        return context

    def get_queryset(self):
        user = (
            EmailUser.objects.filter(id=self.request.user.pk)
            .select_related("business")
            .prefetch_related("business__contacts")
            .first()
        )
        # queryset = BusinessAddress.objects.filter(business=user.get_business())
        queryset = user.business.contacts.all()
        return queryset
