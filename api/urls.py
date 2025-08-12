from django.urls import path,include
from rest_framework.routers import DefaultRouter
from campaigns.views import CampaignViewSet

router = DefaultRouter()
router.register('campaigns', CampaignViewSet, basename='campaign')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
]

