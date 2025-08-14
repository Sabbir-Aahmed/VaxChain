from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from users.models import User,PatientProfile,DoctorProfile
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            'id', 'email', 'nid', 'role', 'password', 'first_name', 'last_name', 'contact_number','profile_image'
        ]

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = 'CustomUser'
        model = User
        fields =[ 
            'id', 'email', 'nid', 'role', 'first_name', 'last_name', 'contact_number', 'profile_image'
        ]
        read_only_fields = ['nid', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'specialization', 'contact_number'
        ]


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = [
            'id','user','blood_type','allergies','medical_conditions','created_at','updated_at'
        ]

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DoctorProfile
        fields = [
            'id','user','specialization','license_number','hospital','bio','created_at','updated_at'
        ]