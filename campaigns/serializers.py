from rest_framework import serializers
from .models import VaccineCampaign, VaccineSchedule
from django.utils import timezone
from bookings.models import VaccineRecord


class VaccineScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineSchedule
        fields = ['id', 'campaign', 'date', 'available_slots', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically limit the campaign field if passed in context
        campaign = self.context.get('campaign')
        if campaign:
            self.fields['campaign'].queryset = VaccineCampaign.objects.filter(pk=campaign.pk)
        else:
            self.fields['campaign'].queryset = VaccineCampaign.objects.filter(status=VaccineCampaign.ACTIVE)

class VaccineCampaignSerializer(serializers.ModelSerializer):
    schedules = VaccineScheduleSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    campaign_image = serializers.ImageField(required=False)

    class Meta:
        model = VaccineCampaign
        fields = [
            'id', 'name','campaign_image','description','is_premium', 'premium_price','vaccine_type','location', 'start_date','end_date','schedules', 'dosage_interval_days', 'max_participants',
              'created_by','status','created_at','updated_at'
        ]
        read_only_fields = ['created_by']
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data



class CampaignBookingSerializer(serializers.Serializer):
    """
    Simple create-only serializer for booking via:
      POST /api/campaigns/{id}/booking/
    Accepts:
      - first_dose_schedule_id (required)
      - campaign_id (optional; URL campaign is used when present)
    """
    campaign_id = serializers.PrimaryKeyRelatedField(
        queryset=VaccineCampaign.objects.filter(status__in=[VaccineCampaign.ACTIVE, VaccineCampaign.UPCOMING]),
        required=False,
        write_only=True
    )
    first_dose_schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=VaccineSchedule.objects.none(),
        write_only=True,
        source='first_dose_schedule'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campaign = self.context.get('campaign')
        today = timezone.now().date()
        if campaign:
            self.fields['first_dose_schedule_id'].queryset = VaccineSchedule.objects.filter(
                campaign=campaign,
                date__gte=today
            )
        else:
            self.fields['first_dose_schedule_id'].queryset = VaccineSchedule.objects.filter(date__gte=today)

    def validate(self, attrs):
        request = self.context.get('request')
        campaign = self.context.get('campaign') or attrs.get('campaign_id')
        schedule = attrs.get('first_dose_schedule')

        if campaign is None:
            raise serializers.ValidationError("Campaign must be provided via the URL or campaign_id.")

        if campaign.status not in [VaccineCampaign.ACTIVE, VaccineCampaign.UPCOMING]:
            raise serializers.ValidationError("This campaign is not open for booking.")

        if schedule.campaign_id != campaign.id:
            raise serializers.ValidationError("Selected schedule does not belong to the selected campaign.")

        if schedule.date < timezone.now().date():
            raise serializers.ValidationError("Cannot book a date in the past.")

        if schedule.available_slots <= 0:
            raise serializers.ValidationError("No available slots for this schedule.")

        if VaccineRecord.objects.filter(patient=request.user, campaign=campaign).exists():
            raise serializers.ValidationError("You already have a booking for this campaign.")

        return attrs