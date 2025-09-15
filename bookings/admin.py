from django.contrib import admin
from bookings.models import VaccineRecord, CampaignReview, Payment

admin.site.register(VaccineRecord)
admin.site.register(CampaignReview)
admin.site.register(Payment)
