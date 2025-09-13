from django.urls import path,include
from rest_framework_nested import routers
from campaigns.views import VaccineCampaignViewSet,VaccineScheduleViewSet
from bookings.views import VaccineBookingViewSet,CampaignReviewViewSet, CampaignBookingSchedulesView
from users.views import PatientProfileViewSet, DoctorProfileViewSet


router = routers.DefaultRouter()
router.register('campaigns', VaccineCampaignViewSet, basename='campaign')
router.register('bookings', VaccineBookingViewSet, basename='bookings')
router.register('patient/profile', PatientProfileViewSet, basename='patient-profile')
router.register('doctor/profile', DoctorProfileViewSet, basename='doctor-profile')
router.register('reviews', CampaignReviewViewSet, basename='reviews')

campaign_router = routers.NestedDefaultRouter(router, 'campaigns', lookup='campaigns')
campaign_router.register('schedule', VaccineScheduleViewSet, basename='schedule')
campaign_router.register('book', CampaignBookingSchedulesView, basename='campaign-book')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(campaign_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
]

