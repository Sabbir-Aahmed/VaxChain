from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import VaccineCampaignSerializer, VaccineScheduleSerializer
from users.permissions import IsDoctor,IsPatient
from .models import VaccineCampaign,VaccineSchedule
from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework import status

from rest_framework.exceptions import PermissionDenied
from users.models import User

class VaccineCampaignViewSet(ModelViewSet):
    queryset = VaccineCampaign.objects.all()
    serializer_class = VaccineCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_schedule']:
            return [IsAuthenticated(), IsDoctor()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.role == User.Role.DOCTOR:
            return queryset.filter(created_by=self.request.user.doctor_profile)
        
        elif self.request.user.role == User.Role.PATIENT:
            return queryset.filter(status='ACTIVE')
        
        return queryset.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can create campaigns")
        serializer.save(created_by=self.request.user.doctor_profile)
    
    def perform_update(self, serializer):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can update campaigns")
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user.role != User.Role.DOCTOR:
            raise PermissionDenied("Only doctors can delete campaigns")
        instance.delete()
    
    @action(detail=True, methods=['post'], serializer_class=VaccineScheduleSerializer)
    def add_schedule(self, request, pk=None):
        campaign = self.get_object()
        if request.user.role != User.Role.DOCTOR:
            return Response(
                {"error": "Only doctors can add schedules"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(campaign=campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VaccineScheduleViewSet(ModelViewSet):
    serializer_class = VaccineScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == User.Role.DOCTOR:
            return VaccineSchedule.objects.filter(campaign__created_by=self.request.user.doctor_profile)
        return VaccineSchedule.objects.filter(campaign__status='ACTIVE')
    
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