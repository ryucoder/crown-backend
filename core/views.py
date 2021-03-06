from django.shortcuts import render

from rest_framework import viewsets

from core.models import State, OrderOption
from core.serializers import StateSerializer, OrderOptionSerializer


class StateViewset(viewsets.ReadOnlyModelViewSet):

    serializer_class = StateSerializer

    def get_queryset(self):
        queryset = State.objects.all()
        return queryset


class OrderOptionViewset(viewsets.ReadOnlyModelViewSet):

    serializer_class = OrderOptionSerializer

    def get_queryset(self):
        queryset = OrderOption.objects.all()
        return queryset
