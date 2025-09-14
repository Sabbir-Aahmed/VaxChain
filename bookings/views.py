from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import VaccineRecord, CampaignReview
from .serializers import VaccineRecordSerializer, CampaignReviewSerializer
from users.permissions import IsPatient, IsDoctor, IsPatientOrReadOnly
from campaigns.models import VaccineSchedule, VaccineCampaign
from rest_framework.decorators import action
from django.db.models import F
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from campaigns.serializers import VaccineScheduleSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet


class VaccineBookingViewSet(ReadOnlyModelViewSet):
    """
    Read-only viewset for listing/retrieving VaccineRecords.
    All booking creation is handled inside VaccineCampaignViewSet (campaigns/{id}/booking/).
    """
    queryset = VaccineRecord.objects.select_related(
        'patient', 'campaign', 'first_dose_schedule', 'first_dose_schedule__campaign','payment',
        'second_dose_schedule', 'second_dose_schedule__campaign'
    ).prefetch_related('campaign__schedules')

    serializer_class = VaccineRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Patients see their own bookings; doctors can see all
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), (IsPatient | IsDoctor)()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset
        if getattr(user, 'role', None) == 'PATIENT':
            qs = qs.filter(patient=user)
        return qs
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsPatient])
    def delete(self, request, pk=None):
        record = self.get_object()
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CampaignReviewViewSet(ModelViewSet):
    queryset = CampaignReview.objects.all()
    serializer_class = CampaignReviewSerializer
    permission_classes = [IsPatientOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset().select_related('patient', 'campaign')
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @swagger_auto_schema(
        operation_summary="List Campaign Reviews",
        operation_description="Retrieve campaign reviews, optionally filtered by campaign_id",
        responses={200: CampaignReviewSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Campaign Review",
        operation_description="Retrieve details of a single campaign review",
        responses={200: CampaignReviewSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Campaign Review",
        operation_description="Submit a review for a campaign (Patient only)",
        request_body=CampaignReviewSerializer,
        responses={201: CampaignReviewSerializer(), 400: 'Bad Request'}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Campaign Review",
        operation_description="Update an existing campaign review",
        request_body=CampaignReviewSerializer,
        responses={200: CampaignReviewSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial Update a Campaign Review",
        operation_description="Partially update an existing campaign review",
        request_body=CampaignReviewSerializer,
        responses={200: CampaignReviewSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Campaign Review",
        operation_description="Delete a campaign review",
        responses={204: 'No Content', 403: 'Permission Denied'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class CampaignBookingSchedulesView(ModelViewSet):
    """
    Endpoint to list available first-dose schedules for a specific campaign during booking.
    Only returns schedules for the given campaign with available slots and future dates.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VaccineScheduleSerializer

    def get_queryset(self):
        campaign_id = self.kwargs.get('campaign_pk')  # Extract campaign ID from URL
        try:
            campaign = VaccineCampaign.objects.get(
                id=campaign_id,
                status=VaccineCampaign.ACTIVE
            )
        except VaccineCampaign.DoesNotExist:
            return VaccineSchedule.objects.none()  # Return empty queryset if campaign invalid

        # Only return schedules for this campaign, with slots > 0, future dates
        return VaccineSchedule.objects.filter(
            campaign=campaign,
            available_slots__gt=0,
            date__gte=timezone.now().date()
        ).select_related('campaign').order_by('date', 'start_time')

    @swagger_auto_schema(
        operation_summary="List Available Schedules for Campaign Booking",
        operation_description="Retrieve available first-dose schedules for a specific campaign (for booking UI). Only shows active campaigns with available slots and future dates.",
        responses={200: VaccineScheduleSerializer(many=True), 404: 'Campaign not found or not active'}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {'detail': 'No available schedules for this campaign or campaign is not active.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().list(request, *args, **kwargs)