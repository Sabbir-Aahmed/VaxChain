from rest_framework import serializers
from .models import VaccineRecord, CampaignReview
from campaigns.models import VaccineSchedule, VaccineCampaign
from campaigns.serializers import VaccineScheduleSerializer,VaccineCampaignSerializer
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
            'id','patient_name','campaign_name','campaign_start_date','campaign_end_date','first_dose_schedule',
            'second_dose_schedule'
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

class VaccineRecordCreateSerializer(serializers.ModelSerializer):
    campaign_id = serializers.PrimaryKeyRelatedField(
        queryset=VaccineCampaign.objects.filter(status=VaccineCampaign.ACTIVE),
        write_only=True
    )
    first_dose_schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=VaccineSchedule.objects.all(),
        write_only=True,
        source='first_dose_schedule'
    )

    class Meta:
        model = VaccineRecord
        fields = ['campaign_id', 'first_dose_schedule_id']

    def validate(self, attrs):
        request = self.context.get('request')
        campaign = attrs.get('campaign_id')
        schedule = attrs.get('first_dose_schedule')

        if schedule.date < timezone.now().date():
            raise serializers.ValidationError("Cannot book a date in the past.")
        if schedule.available_slots <= 0:
            raise serializers.ValidationError("No available slots for this schedule.")
        if schedule.campaign != campaign:
            raise serializers.ValidationError("Selected schedule does not belong to the selected campaign.")
        if VaccineRecord.objects.filter(patient=request.user, campaign=campaign).exists():
            raise serializers.ValidationError("You already have a booking for this campaign.")

        return attrs

class CampaignReviewSerializer(serializers.ModelSerializer):
    patient = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = CampaignReview
        fields = '__all__'
        read_only_fields = ['patient']
    
    def validate(self, data):
        patient = self.context['request'].user.patient_profile
        if not VaccineRecord.objects.filter(patient=patient, campaign=data['campaign']).exists():
            raise serializers.ValidationError("You must book this vaccine to review it")
        return data