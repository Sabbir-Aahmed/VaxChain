from django.db import models
from campaigns.models import VaccineCampaign
from django.conf import settings
from datetime import timedelta

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               limit_choices_to={'role': 'PATIENT'})
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE)
    first_dose_date = models.DateField()
    second_dose_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('patient', 'campaign')
        ordering = ['-booked_at']

    def __str__(self):
        return f"{self.patient.email} - {self.campaign.name}"
