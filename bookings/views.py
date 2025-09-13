from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from .models import VaccineRecord, CampaignReview
from .serializers import VaccineRecordSerializer, CampaignReviewSerializer, VaccineRecordCreateSerializer
from users.permissions import IsPatient, IsDoctor, IsPatientOrReadOnly
from django.db import transaction
from campaigns.models import VaccineSchedule, VaccineCampaign
from rest_framework.decorators import action
from django.db.models import F
from drf_yasg.utils import swagger_auto_schema

class VaccineBookingViewSet(ModelViewSet):
    queryset = VaccineRecord.objects.select_related(
        'patient', 'campaign', 'first_dose_schedule', 'first_dose_schedule__campaign',
        'second_dose_schedule', 'second_dose_schedule__campaign'
    ).prefetch_related('campaign__schedules',)

    lookup_field = 'id'

    def get_permissions(self):
        # Early block for non-POST on nested route
        if self.kwargs.get('campaigns_pk') and self.request.method != 'POST':
            # Permissions check runs before queryset, so raise here
            raise MethodNotAllowed({'detail': f'{self.request.method} not supported on this nested route. Use POST to book.'})
        
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
        # Early block for nested GET: Prevent DRF's internal filtering from raising FieldError
        if self.kwargs.get('campaigns_pk') and self.request.method == 'GET':
            raise MethodNotAllowed({'detail': 'GET not supported. Use POST to book or /bookings/ to list all.'})

        user = self.request.user
        query_set = self.queryset
        if getattr(user, 'role', None) == 'PATIENT':
            query_set = query_set.filter(patient=user)

        campaigns_pk = self.kwargs.get('campaigns_pk')
        if campaigns_pk:
            query_set = query_set.filter(campaign_id=campaigns_pk)
        return query_set

    @swagger_auto_schema(
        operation_summary="Create a Vaccine Booking",
        operation_description="Book a vaccine slot for the first dose via a campaign. Automatically decrements available slots. URL: /campaigns/{campaigns_pk}/book/",
        request_body=VaccineRecordCreateSerializer,
        responses={201: VaccineRecordSerializer(), 400: 'Bad Request', 404: 'Not Found'}
    )
    def create(self, request, *args, **kwargs):
        campaigns_pk = self.kwargs.get('campaigns_pk')
        if not campaigns_pk:
            return Response({'detail': 'Campaign ID required in URL.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            campaign = VaccineCampaign.objects.get(pk=campaigns_pk)
        except VaccineCampaign.DoesNotExist:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)

        if campaign.status != VaccineCampaign.ACTIVE:
            return Response({'detail': 'Campaign is not active for booking.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={
            'request': request,
            'campaign_id': campaign.id
        })
        serializer.is_valid(raise_exception=True)

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

                VaccineSchedule.objects.filter(pk=locked_schedule.pk).update(
                    available_slots=F('available_slots') - 1
                )

                output_serializer = VaccineRecordSerializer(record, context={'request': request})
                return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except VaccineSchedule.DoesNotExist:
            return Response({'detail': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        # Fixed: Correct MethodNotAllowed signature (dict for detail)
        if self.kwargs.get('campaigns_pk') and self.action != 'create':
            raise MethodNotAllowed({'detail': f'{self.action.upper()} not supported on this nested route'})
        return super().get_object()
    
    @swagger_auto_schema(
        operation_summary="List Vaccine Bookings",
        operation_description="Retrieve a list of vaccine bookings for the logged-in user or for doctors (use /bookings/ instead for this nested route)",
        responses={200: VaccineRecordSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        # Redundant now (blocked earlier), but kept for safety
        if self.kwargs.get('campaigns_pk'):
            raise MethodNotAllowed({'detail': 'GET not supported. Use POST to book or /bookings/ to list all.'})
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Vaccine Booking",
        operation_description="Retrieve details of a single vaccine booking",
        responses={200: VaccineRecordSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Vaccine Booking",
        operation_description="Cancel a vaccine booking (Patient only)",
        responses={204: 'No Content', 403: 'Permission Denied'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# CampaignReviewViewSet remains unchanged
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
        responses={200: VaccineRecordSerializer()}
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