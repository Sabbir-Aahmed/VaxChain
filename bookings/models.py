from django.db import models
from campaigns.models import VaccineCampaign
from django.conf import settings
from datetime import timedelta

class Booking(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"rolse": "PATIENT"})
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name="booking")
    first_dose_date = models.DateField()
    second_dose_date = models.DateField()
    booked_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    class Meta:
        unique_together = ('patient' , 'campaign')


    def save(self,*args,**kwargs):
        if not self.second_dose_date:
            self.second_dose_date = self.first_dose_date + timedelta(days=self.campaign.dose_interval_days)
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.patient.email} - {self.campaign.name} - ({self.payment_status})"
