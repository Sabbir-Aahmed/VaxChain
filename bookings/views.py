from rest_framework import status
from django.db import models
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta
from .models import VaccineRecord, CampaignReview
from .serializers import VaccineRecordSerializer,CampaignReviewSerializer, VaccineRecordCreateSerializer
from users.permissions import IsPatient,IsDoctor
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError
from django.db import transaction
from users.models import User
from campaigns.models import VaccineCampaign,VaccineSchedule
from campaigns.serializers import VaccineCampaignSerializer,VaccineScheduleSerializer
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Prefetch,F


class VaccineBookingViewSet(ModelViewSet):
    queryset = VaccineRecord.objects.select_related(
        'patient','campaign','first_dose_schedule','first_dose_schedule__campaign','second_dose_schedule','second_dose_schedule__campaign'
    ).prefetch_related('campaign__schedules',)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsPatient()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), (IsPatient | IsDoctor)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return VaccineRecordCreateSerializer
        return VaccineRecordSerializer

    def get_queryset(self):
        user = self.request.user
        query_set = self.queryset
        if getattr(user, 'role', None) == 'PATIENT':
            query_set=query_set.filter(patient=user)
        return query_set


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        campaign = serializer.validated_data['campaign_id']
        schedule = serializer.validated_data['first_dose_schedule']
        user = request.user

        try:
            with transaction.atomic():
                locked_schedule = VaccineSchedule.objects.select_for_update().select_related('campaign').get(pk=schedule.pk)

                if locked_schedule.available_slots <= 0:
                    return Response({'detail': 'No available slots.'}, status=status.HTTP_400_BAD_REQUEST)

                record = VaccineRecord.objects.create(
                    patient=user,
                    campaign=campaign,
                    first_dose_schedule=locked_schedule,
                    status=VaccineRecord.SCHEDULED
                )
                
                VaccineSchedule.objects.filter(pk=locked_schedule.pk).update(available_slots=F('available_slots') - 1)

                output_serializer = VaccineRecordCreateSerializer(record, context={'request': request})
                return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except VaccineSchedule.DoesNotExist:
            return Response({'detail': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

class CampaignReviewViewSet(ModelViewSet):
    serializer_class = CampaignReviewSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    
    def get_queryset(self):
        if self.request.user.role == User.PATIENT:
            return CampaignReview.objects.filter(patient=self.request.user.patient_profile)
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            return CampaignReview.objects.filter(campaign_id=campaign_id)
        return CampaignReview.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != User.PATIENT:
            raise PermissionDenied("Only patients can leave reviews")
        serializer.save(patient=self.request.user.patient_profile)