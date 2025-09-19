from rest_framework import serializers
from .models import VaccineRecord, CampaignReview, Payment
from campaigns.models import VaccineSchedule, VaccineCampaign

from django.utils import timezone
from django.db import transaction

class VaccineRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    campaign_start_date = serializers.DateField(source='campaign.start_date', read_only=True)
    campaign_end_date = serializers.DateField(source='campaign.end_date', read_only=True)
    first_dose_schedule = serializers.SerializerMethodField()
    second_dose_schedule = serializers.SerializerMethodField()

    class Meta:
        model = VaccineRecord
        fields = [
            'id', 'patient_name', 'campaign_name', 'campaign_start_date', 'campaign_end_date',
            'first_dose_schedule', 'second_dose_schedule', "created_at", "updated_at",
        ]

    def get_first_dose_schedule(self, obj):
        if obj.first_dose_schedule:
            return {
                'id': obj.first_dose_schedule.id,
                'date': obj.first_dose_schedule.date,
                'start_time': obj.first_dose_schedule.start_time,
                'end_time': obj.first_dose_schedule.end_time
            }
        return None

    def get_second_dose_schedule(self, obj):
        if obj.second_dose_schedule:
            return {
                'id': obj.second_dose_schedule.id,
                'date': obj.second_dose_schedule.date,
                'start_time': obj.second_dose_schedule.start_time,
                'end_time': obj.second_dose_schedule.end_time
            }
        return None


class CampaignReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField(read_only=True)
    campaign_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CampaignReview
        fields = ['id', 'patient_name', 'campaign_name',
                  'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['patient_name', 'campaign_name', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()

    def get_campaign_name(self, obj):
        return obj.campaign.name
    
    
class PaymentInitiateSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    cus_name = serializers.CharField(required=False, allow_blank=True)
    cus_address = serializers.CharField(required=False, allow_blank=True)
    cus_phone = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        try:
            payment = Payment.objects.get(id=attrs['payment_id'])
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found.")

        if str(payment.amount) != str(attrs['amount']):
            raise serializers.ValidationError("Amount mismatch with payment record.")

        attrs['payment'] = payment
        return attrs