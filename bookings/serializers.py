from rest_framework import serializers,status
from rest_framework.serializers import ValidationError
from .models import Booking
from django.utils import timezone

class BookingSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id','patient', 'campaign','campaign_name','first_dose_date','second_dose_date','status','booked_at', 'updated_at'
        ]

        read_only_fields = ['patient', 'second_dose_date', 'booked_at', 'status']
    


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['first_dose_date']
        extra_kwargs = {
            'first_dose_date': {'required': True}
        }

    def validate(self, data):
        request = self.context.get('request')
        campaign = self.context.get('campaign') 
        first_dose_date = data['first_dose_date']

        if Booking.objects.filter(patient=request.user, campaign=campaign).exists():
            raise ValidationError("You already have a booking for this campaign")

        if not (campaign.start_date <= first_dose_date <= campaign.end_date):
            raise ValidationError(
                f"Date must be between {campaign.start_date} and {campaign.end_date}"
            )

        if first_dose_date < timezone.now().date():
            raise ValidationError("Cannot book dates in the past")

        return data

    def create(self, validated_data):
        campaign = self.context.get('campaign')
        request = self.context.get('request')

        return Booking.objects.create(
            patient=request.user,
            campaign=campaign,
            first_dose_date=validated_data['first_dose_date'],
            status='PENDING'
        )