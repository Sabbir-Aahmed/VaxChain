from django.urls import path,include
from rest_framework_nested import routers
from campaigns.views import VaccineCampaignViewSet,VaccineScheduleViewSet
from bookings.views import VaccineBookingViewSet
from users.views import PatientProfileViewSet, DoctorProfileViewSet


router = routers.DefaultRouter()
router.register('campaigns', VaccineCampaignViewSet, basename='campaign')
router.register('bookings', VaccineBookingViewSet, basename='bookings')
router.register('patient/profile', PatientProfileViewSet, basename='patient-profile')
router.register('doctor/profile', DoctorProfileViewSet, basename='doctor-profile')

cmapaign_router = routers.NestedDefaultRouter(router, 'campaigns', lookup = 'campaigns')
cmapaign_router.register('schedule', VaccineScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cmapaign_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
]

