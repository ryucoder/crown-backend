from django.shortcuts import render

from rest_framework import viewsets

from businesses.serializers import BusinessSerializer
from businesses.models import Business


class BusinessViewset(viewsets.ModelViewSet):

    serializer_class = BusinessSerializer

    def get_queryset(self):
        queryset = Business.objects.all().prefetch_related(
            "contacts", "addresses", "accounts"
        )
        return queryset
