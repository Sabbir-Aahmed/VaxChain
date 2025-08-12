from django.urls import path,include
from rest_framework.routers import DefaultRouter
from campaigns.views import CampaignViewSet
from bookings.views import BookingViewSet


router = DefaultRouter()
router.register('campaigns', CampaignViewSet, basename='campaign')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
]

