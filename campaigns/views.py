from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import VaccineCampaignSerializer, VaccineScheduleSerializer
from users.permissions import IsDoctor,IsPatient
from .models import VaccineCampaign,VaccineSchedule
from django.db.models import Prefetch, Count
from rest_framework.exceptions import PermissionDenied
from users.models import User
from rest_framework.decorators import action


class VaccineCampaignViewSet(ModelViewSet):
    queryset = VaccineCampaign.objects.select_related('created_by').prefetch_related(
        Prefetch('schedules', queryset=VaccineSchedule.objects.order_by('date', 'start_time'))
    )
    serializer_class = VaccineCampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_schedule']:
            return [IsAuthenticated(), IsDoctor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role == User.Role.DOCTOR:
            return qs.filter(created_by=user)
        elif user.role == User.Role.PATIENT:
            return qs.filter(status=VaccineCampaign.ACTIVE)
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

    
class VaccineScheduleViewSet(ModelViewSet):
    queryset = VaccineSchedule.objects.select_related('campaign', 'campaign__created_by')
    serializer_class = VaccineScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.role == User.Role.DOCTOR:
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