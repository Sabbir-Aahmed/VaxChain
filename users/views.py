from django.shortcuts import render
from rest_framework import status
from .serializers import PatientProfileSerializer,DoctorProfileSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPatient, IsDoctor
from rest_framework.viewsets import ModelViewSet
from .models import PatientProfile, DoctorProfile


class PatientProfileViewSet(ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsPatient]

    def get_queryset(self):
        return PatientProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.patient_profile

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DoctorProfileViewSet(ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return DoctorProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.doctor_profile

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)