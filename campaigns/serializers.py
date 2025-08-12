from rest_framework import serializers
from .models import VaccineCampaign, VaccineSchedule

class VaccineScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineSchedule
        fields = [
            'id', 'campaign', 'date', 'available_slots', 'start_time', 'end_time', 'created_at','updated_at'
        ]

class VaccineCampaignSerializer(serializers.ModelSerializer):
    schedules = VaccineScheduleSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    
    class Meta:
        model = VaccineCampaign
        fields = [
            'id', 'name','description','vaccine_type', 'start_date','end_date','schedules', 'dosage_interval_days', 'max_participants',
              'created_by','status','created_at','updated_at'
        ]
        read_only_fields = ['created_by', 'status']
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data