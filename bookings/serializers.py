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