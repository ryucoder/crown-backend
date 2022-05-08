from django.shortcuts import render

from rest_framework import viewsets

from core.models import State, JobType
from core.serializers import StateSerializer, JobTypeSerializer


class StateViewset(viewsets.ReadOnlyModelViewSet):

    serializer_class = StateSerializer

    def get_queryset(self):
        queryset = State.objects.all()
        return queryset


class JobTypeViewset(viewsets.ReadOnlyModelViewSet):

    serializer_class = JobTypeSerializer

    def get_queryset(self):
        queryset = JobType.objects.all()
        return queryset
