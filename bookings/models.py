from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from users.models import PatientProfile
from campaigns.models import VaccineCampaign, VaccineSchedule

class VaccineRecord(models.Model):
    SCHEDULED = 'SCHEDULED'
    COMPLETED = 'COMPLETED'
    MISSED = 'MISSED'
    
    STATUS_CHOICES = [
        (SCHEDULED, 'Scheduled'),
        (COMPLETED, 'Completed'),
        (MISSED, 'Missed'),
    ]
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='vaccine_records')
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE)
    first_dose_schedule = models.ForeignKey( VaccineSchedule, on_delete=models.CASCADE, related_name='first_dose_bookings')
    second_dose_schedule = models.ForeignKey(VaccineSchedule, on_delete=models.CASCADE, related_name='second_dose_bookings',null=True,blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.campaign.name}"

class CampaignReview(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reviews')
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('patient', 'campaign')
    
    def __str__(self):
        return f"Review by {self.patient.user.username} for {self.campaign.name}"