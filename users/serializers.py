from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from users.models import User
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            'id', 'email', 'nid', 'role', 'password', 'first_name', 'last_name', 'contact_number','profile_image'
        ]

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields =[ 
            'id', 'email', 'nid', 'role', 'first_name', 'last_name', 'specialization', 'contact_number', 'profile_image'
        ]
        read_only_fields = ['nid', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.role == 'PATIENT':
            self.fields.pop('specialization')

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'specialization', 'contact_number'
        ]