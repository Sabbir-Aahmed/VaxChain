from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import VaccineCampaignSerializer, VaccineScheduleSerializer
from users.permissions import IsDoctor,IsPatient
from .models import VaccineCampaign,VaccineSchedule
from rest_framework.exceptions import PermissionDenied
from users.models import User
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from campaigns.pagination import DefaultPagination


class VaccineCampaignViewSet(ModelViewSet):
    queryset = VaccineCampaign.objects.select_related('created_by').prefetch_related(
        'schedules',
    )
    serializer_class = VaccineCampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields = ['status']
    pagination_class = DefaultPagination
    search_fields = ['name', 'description', 'location','vaccine_type']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_schedule']:
            return [IsAuthenticated(), IsDoctor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()

        user = self.request.user
        qs = super().get_queryset()

        if getattr(user, 'role', None) == User.Role.DOCTOR:
            return qs.filter(created_by=user)
        elif getattr(user, 'role', None) == User.Role.PATIENT:
            return qs
        return qs.none()

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can create campaigns")
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can update campaigns")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can delete campaigns")
        instance.delete()

    @swagger_auto_schema(
        operation_summary="List Vaccine Campaigns",
        operation_description="Retrieve a list of all vaccine campaigns available to the user",
        responses={200: VaccineCampaignSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Vaccine Campaign",
        operation_description="Retrieve detailed information about a single vaccine campaign",
        responses={200: VaccineCampaignSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Vaccine Campaign",
        operation_description="Create a new vaccine campaign (Doctor only)",
        request_body=VaccineCampaignSerializer,
        responses={201: VaccineCampaignSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Vaccine Campaign",
        operation_description="Update a vaccine campaign (Doctor only)",
        request_body=VaccineCampaignSerializer,
        responses={200: VaccineCampaignSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial Update a Vaccine Campaign",
        operation_description="Partially update a vaccine campaign (Doctor only)",
        request_body=VaccineCampaignSerializer,
        responses={200: VaccineCampaignSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Vaccine Campaign",
        operation_description="Delete a vaccine campaign (Doctor only)",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class VaccineScheduleViewSet(ModelViewSet):
    queryset = VaccineSchedule.objects.select_related('campaign', 'campaign__created_by')
    serializer_class = VaccineScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()

        user = self.request.user
        qs = super().get_queryset()

        if getattr(user, 'role', None) == User.Role.DOCTOR:
            return qs.filter(campaign__created_by=user)
        return qs.filter(campaign__status=VaccineCampaign.ACTIVE)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can create schedules")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can update schedules")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can delete schedules")
        instance.delete()

    @swagger_auto_schema(
        operation_summary="List Vaccine Schedules",
        operation_description="Retrieve a list of vaccine schedules available to the user",
        responses={200: VaccineScheduleSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Vaccine Schedule",
        operation_description="Retrieve detailed information about a single vaccine schedule",
        responses={200: VaccineScheduleSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Vaccine Schedule",
        operation_description="Create a new vaccine schedule (Doctor only)",
        request_body=VaccineScheduleSerializer,
        responses={201: VaccineScheduleSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Vaccine Schedule",
        operation_description="Update a vaccine schedule (Doctor only)",
        request_body=VaccineScheduleSerializer,
        responses={200: VaccineScheduleSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial Update a Vaccine Schedule",
        operation_description="Partially update a vaccine schedule (Doctor only)",
        request_body=VaccineScheduleSerializer,
        responses={200: VaccineScheduleSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Vaccine Schedule",
        operation_description="Delete a vaccine schedule (Doctor only)",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)