from django.urls import path,include
from rest_framework.routers import DefaultRouter
from campaigns.views import VaccineCampaignViewSet
from bookings.views import BookingViewSet
from users.views import PatientProfileViewSet, DoctorProfileViewSet


router = DefaultRouter()
router.register('campaigns', VaccineCampaignViewSet, basename='campaign')
router.register('bookings', BookingViewSet, basename='booking')
router.register('patient/profile', PatientProfileViewSet, basename='patient-profile')
router.register('doctor/profile', DoctorProfileViewSet, basename='doctor-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
]

