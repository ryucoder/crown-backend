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
    ToggleDefaultBusinessAddressSerializer,
    OrderSerializer,
)
from businesses.models import Business, BusinessAccount, BusinessAddress, Order


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

    def get_queryset(self):
        queryset = (
            Order.objects.all().order_by("-created_at").prefetch_related("options")
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(from_user_id=self.request.user.id)


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
        # queryset = BusinessAddress.objects.filter(business=user.get_business())
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
