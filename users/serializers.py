from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from users.models import User

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
        read_only_fields = ['nid']