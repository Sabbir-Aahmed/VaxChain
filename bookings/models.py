from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from campaigns.models import VaccineCampaign, VaccineSchedule
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class VaccineRecord(models.Model):
    SCHEDULED = 'SCHEDULED'
    COMPLETED = 'COMPLETED'
    MISSED = 'MISSED'
    
    STATUS_CHOICES = [
        (SCHEDULED, 'Scheduled'),
        (COMPLETED, 'Completed'),
        (MISSED, 'Missed'),
    ]
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vaccine_records')
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE)
    first_dose_schedule = models.ForeignKey(VaccineSchedule, on_delete=models.CASCADE, related_name='first_dose_bookings')
    second_dose_schedule = models.ForeignKey(VaccineSchedule, on_delete=models.CASCADE, related_name='second_dose_bookings',null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.second_dose_schedule and self.first_dose_schedule:
            gap_days = self.campaign.dosage_interval_days
            second_dose_date = self.first_dose_schedule.date + timedelta(days=gap_days)
            
            second_schedule = VaccineSchedule.objects.filter(
                campaign=self.campaign,
                date=second_dose_date
            ).first()
            
            if not second_schedule:
                second_schedule = VaccineSchedule.objects.create(
                    campaign=self.campaign,
                    date=second_dose_date,
                    available_slots=10,
                    start_time=self.first_dose_schedule.start_time,
                    end_time=self.first_dose_schedule.end_time
                )
            
            self.second_dose_schedule = second_schedule
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.campaign.name}"

class CampaignReview(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('patient', 'campaign')
    
    def __str__(self):
        return f"Review by {self.patient.user.get_full_name()} for {self.campaign.name}"