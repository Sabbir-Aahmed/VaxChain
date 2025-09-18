from rest_framework import status
from django.shortcuts import redirect
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import VaccineRecord, CampaignReview,Payment
from .serializers import VaccineRecordSerializer, CampaignReviewSerializer, PaymentInitiateSerializer
from users.permissions import IsPatient, IsDoctor, IsPatientOrReadOnly
from campaigns.models import VaccineSchedule, VaccineCampaign
from rest_framework.decorators import action
from django.db.models import F
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from campaigns.serializers import VaccineScheduleSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view
from sslcommerz_lib import SSLCOMMERZ 
from decouple import config
from django.conf import settings as main_settings
from rest_framework.views import APIView

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
        if getattr(self, 'swagger_fake_view', False):
            return VaccineRecord.objects.none()
        user = self.request.user
        qs = self.queryset
        if getattr(user, 'role', None) == 'PATIENT':
            qs = qs.filter(patient=user)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsPatient])
    def delete(self, request, pk=None):
        record = self.get_object()
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.response import Response

class CampaignReviewViewSet(ModelViewSet):
    queryset = CampaignReview.objects.all()
    serializer_class = CampaignReviewSerializer
    permission_classes = [IsPatientOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CampaignReview.objects.none()
        queryset = super().get_queryset().select_related('patient', 'campaign')
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @swagger_auto_schema(
        operation_summary="List Campaign Reviews",
        operation_description="Retrieve campaign reviews with total count, optionally filtered by campaign_id",
        responses={200: '{"count": 10, "results": [...]}'}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        queryset = self.filter_queryset(self.get_queryset())
        response.data = {
            'count': queryset.count(),
            'results': response.data
        }
        return response

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


@api_view(['POST'])
def initiate_payment(request):
    print(request.data)
    serializer = PaymentInitiateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    payment = serializer.validated_data['payment']
    cus_name = serializer.validated_data.get('cus_name') or payment.patient.get_full_name()
    cus_address = serializer.validated_data.get('cus_address') or getattr(payment.patient, "address", "")
    cus_phone = serializer.validated_data.get('cus_phone') or getattr(payment.patient, "contact_number", "")
    amount = serializer.validated_data['amount']


    settings = { 'store_id': config('Store_ID'), 'store_pass': config('store_pass'), 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f"txn_{payment.id}"
    post_body['success_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/success/"
    post_body['fail_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/fail/"
    post_body['cancel_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/cancel/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = cus_name
    post_body['cus_email'] = payment.patient.email,
    post_body['cus_phone'] = cus_phone
    post_body['cus_add1'] = cus_address
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Medical Product"
    post_body['product_category'] = "Vaccine"
    post_body['product_profile'] = "general"

    response = sslcz.createSession(post_body) # API response
    print("SSLCommerz response:", response)
    if response.get("status") == 'SUCCESS':
        return Response({"payment_url": response['GatewayPageURL']})
    return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def payment_success(request):
    payemnt_id = request.data.get("tran_id").split('_')[1]
    payment = Payment.objects.get(id=payemnt_id)
    payment.payment_status = Payment.SUCCESS
    payment.payment_reference = request.data.get("bank_tran_id")
    payment.save()

    # Create VaccineRecord after payment
    from campaigns.models import VaccineCampaign, VaccineSchedule
    campaign = VaccineCampaign.objects.get(id=payment.campaign_id)
    schedule = VaccineSchedule.objects.get(id=payment.schedule_id)

    record = VaccineRecord.objects.create(
        patient=payment.patient,
        campaign=campaign,
        first_dose_schedule=schedule,
        status=VaccineRecord.SCHEDULED
    )

    # Link payment to the created record
    payment.record = record
    payment.save()

    # Reduce slot count
    schedule.available_slots = F('available_slots') - 1
    schedule.save()

    return redirect(f"{main_settings.FRONTEND_URL}/dashboard/user")

@api_view(['POST'])
def payment_cancel(request):
    return redirect(f"{main_settings.FRONTEND_URL}/dashboard/user")


@api_view(['POST'])
def payment_fail(request):
    tran_id = request.data.get("tran_id")
    if tran_id and tran_id.startswith("txn_"):
        payment_id = tran_id.split('_')[1]
        Payment.objects.filter(id=payment_id).update(payment_status=Payment.FAILED)
    return redirect(f"{main_settings.FRONTEND_URL}/dashboard/user")