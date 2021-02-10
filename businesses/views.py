from django.shortcuts import render

from rest_framework import viewsets

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
    JWTTokenUserAuthentication,
)

from core.utils import CurrentPagePagination

from businesses.serializers import BusinessSerializer, OrderSerializer
from businesses.models import Business, Order


class BusinessViewset(viewsets.ModelViewSet):

    serializer_class = BusinessSerializer

    def get_queryset(self):
        queryset = Business.objects.all().prefetch_related(
            "contacts", "addresses", "accounts"
        )
        return queryset


class OrderViewset(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    pagination_class = CurrentPagePagination
    authentication_classes = [JWTTokenUserAuthentication]

    def get_queryset(self):
        print()
        print()
        print("get_queryset")
        print("self.request.user")
        print(self.request.user)
        print(self.request.user.id)
        print()
        print()
        queryset = Order.objects.all().order_by("-created_at").prefetch_related("options")
        return queryset

    def perform_create(self, serializer):
        print()
        print()
        print("perform_create")
        print("self.request.user")
        print(self.request.user)
        print(self.request.user.id)
        print()
        print()
        serializer.save(from_user_id=self.request.user.id)