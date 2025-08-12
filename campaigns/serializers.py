from rest_framework import serializers
from .models import VaccineCampaign
from users.serializers import DoctorSerializer

class VaccinCampaignSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only = True)

    class Meta: 
        model = VaccineCampaign
        fields = [
            'id','name','description','start_date','end_date','dose_interval_days','created_at','doctor'
        ]

        read_only_fields = ['doctor', 'created_at']