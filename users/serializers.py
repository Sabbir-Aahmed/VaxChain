from rest_framework import serializers
from users.models import User

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = {
            'id', 'email', 'nid', 'role', 'password', 'first_name', 'last_name', 'contact_number' 
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = {
            'id', 'email', 'nid', 'role', 'first_name', 'last_name', 'specialization', 'contact_number', 'profile_picture'
        }