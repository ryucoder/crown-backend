from django.shortcuts import render

from rest_framework import viewsets

from core.utils import CurrentPagePagination, CommonUtil

from businesses.serializers import BusinessSerializer, OrderSerializer
from businesses.models import Business, Order


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
