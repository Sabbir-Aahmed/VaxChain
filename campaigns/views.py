from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import VaccinCampaignSerializer
from users.permissions import IsDoctor,IsPatient
from .models import VaccineCampaign
from rest_framework.decorators import action
from bookings.serializers import BookingCreateSerializer,BookingSerializer
from bookings.models import Booking
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

class CampaignViewSet(ModelViewSet):
    queryset = VaccineCampaign.objects.all()
    serializer_class = VaccinCampaignSerializer

    def get_serializer_class(self):
        if self.action == 'book':
            return BookingCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsDoctor]

        elif self.action == 'book':
            permission_classes = [IsAuthenticated, IsPatient]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        return serializer.save(doctor = self.request.user)
    

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        campaign = self.get_object()

        serializer = self.get_serializer(data=request.data, context={'request': request, 'campaign': campaign})
        serializer.is_valid(raise_exception=True)
        first_dose_date = serializer.validated_data['first_dose_date']

        if Booking.objects.filter(patient=request.user, campaign=campaign).exists():
            return Response(
                {"detail": "You already have a booking for this campaign"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (campaign.start_date <= first_dose_date <= campaign.end_date):
            return Response(
                {"detail": f"Date must be between {campaign.start_date} and {campaign.end_date}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if first_dose_date < timezone.now().date():
            return Response(
                {"detail": "Cannot book dates in the past"},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking = Booking.objects.create(
            patient=request.user,
            campaign=campaign,
            first_dose_date=first_dose_date,
            status='PENDING'
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )