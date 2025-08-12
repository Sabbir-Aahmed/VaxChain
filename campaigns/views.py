from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import VaccinCampaignSerializer
from users.permissions import IsDoctor
from .models import VaccineCampaign

class CampaignViewSet(ModelViewSet):
    queryset = VaccineCampaign.objects.all()
    serializer_class = VaccinCampaignSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partical_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsDoctor]

        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        return serializer.save(doctor = self.request.user)
    

