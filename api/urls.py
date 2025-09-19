from django.urls import path,include
from rest_framework_nested import routers
from campaigns.views import VaccineCampaignViewSet,VaccineScheduleViewSet
from bookings.views import VaccineBookingViewSet,CampaignReviewViewSet,initiate_payment,payment_success,payment_fail,payment_cancel
from users.views import PatientProfileViewSet, DoctorProfileViewSet

router = routers.DefaultRouter()
router.register('campaigns', VaccineCampaignViewSet, basename='campaign')
router.register('bookings', VaccineBookingViewSet, basename='bookings')
router.register('patient/profile', PatientProfileViewSet, basename='patient-profile')
router.register('doctor/profile', DoctorProfileViewSet, basename='doctor-profile')
router.register('reviews', CampaignReviewViewSet, basename='reviews')

campaign_router = routers.NestedDefaultRouter(router, 'campaigns', lookup='campaigns')
campaign_router.register('schedule', VaccineScheduleViewSet, basename='schedule')
campaign_router.register('reviews', CampaignReviewViewSet, basename='campaign-reviews')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(campaign_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('payment/initiate/',initiate_payment, name="initiate_payment" ),
    path('payment/success/',payment_success, name="payment_success" ),
    path('payment/fail/',payment_fail, name="payment_fail" ),
    path('payment/cancel/',payment_cancel, name="payment_cancel" ),
    
]

