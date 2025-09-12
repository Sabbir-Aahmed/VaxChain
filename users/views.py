from django.shortcuts import render
from rest_framework import status
from .serializers import PatientProfileSerializer,DoctorProfileSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPatient, IsDoctor
from rest_framework.viewsets import ModelViewSet
from .models import PatientProfile, DoctorProfile
from drf_yasg.utils import swagger_auto_schema

class PatientProfileViewSet(ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsPatient]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PatientProfile.objects.none()
        return PatientProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.patient_profile

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Get list of patient profiles",
        operation_description="Retrieve all patient profiles for the logged-in user",
        responses={200: PatientProfileSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve patient profile",
        operation_description="Retrieve the logged-in patient's profile",
        responses={200: PatientProfileSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)    
    @swagger_auto_schema(
        operation_summary="Create patient profile",
        operation_description="Create a new patient profile for the logged-in user",
        request_body=PatientProfileSerializer,
        responses={201: PatientProfileSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update patient profile",
        operation_description="Update the logged-in patient's profile",
        request_body=PatientProfileSerializer,
        responses={200: PatientProfileSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)    

    @swagger_auto_schema(
        operation_summary="Partial update patient profile",
        operation_description="Partially update the logged-in patient's profile",
        request_body=PatientProfileSerializer,
        responses={200: PatientProfileSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete patient profile",
        operation_description="Delete the logged-in patient's profile",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DoctorProfileViewSet(ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DoctorProfile.objects.none()
        return DoctorProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return self.request.user.doctor_profile

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Get list of doctor profiles",
        operation_description="Retrieve all doctor profiles for the logged-in user",
        responses={200: DoctorProfileSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve doctor profile",
        operation_description="Retrieve the logged-in doctor's profile",
        responses={200: DoctorProfileSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create doctor profile",
        operation_description="Create a new doctor profile for the logged-in user",
        request_body=DoctorProfileSerializer,
        responses={201: DoctorProfileSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update doctor profile",
        operation_description="Update the logged-in doctor's profile",
        request_body=DoctorProfileSerializer,
        responses={200: DoctorProfileSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update doctor profile",
        operation_description="Partially update the logged-in doctor's profile",
        request_body=DoctorProfileSerializer,
        responses={200: DoctorProfileSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete doctor profile",
        operation_description="Delete the logged-in doctor's profile",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)