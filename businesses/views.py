from django.shortcuts import render

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
)
from businesses.models import Business, BusinessAccount, BusinessContact, Order


class BusinessViewset(viewsets.ModelViewSet):

    serializer_class = BusinessSerializer
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_queryset(self):
        queryset = Business.objects.all().prefetch_related(
            "contacts", "addresses", "accounts"
        )
        return queryset


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
            .select_related("business")
            .first()
        )
        context["action"] = self.action
        return context

    def get_queryset(self):

        user = (
            EmailUser.objects.filter(id=self.request.user.pk)
            .select_related("business")
            .prefetch_related("orders_created", "business__orders_created")
            .first()
        )
        users_business = user.get_business()

        if users_business.category == "dentist":
            if user.user_type == "owner":
                queryset = users_business.orders_created.all()
            if user.user_type == "employee":
                queryset = user.orders_created.all()

        if users_business.category == "laboratory":
            if user.user_type == "owner":
                queryset = users_business.orders_received.all()
            if user.user_type == "employee":
                queryset = user.orders_received.all()

        # dentist
        # owner - from_dentist
        # employee - from_user

        # laboratory
        # owner - to_laboratory
        # employee - to_user

        return queryset


class BusinessAccountViewset(viewsets.ModelViewSet):

    serializer_class = BusinessAccountSerializer
    # pagination_class = CurrentPagePagination
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_permissions(self):
        # For add_business_account
        #   only owner can create accounts

        return super().get_permissions()

    def get_queryset(self):
        user = (
            EmailUser.objects.filter(id=self.request.user.pk)
            .select_related("business")
            .prefetch_related("business__accounts")
            .first()
        )
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
