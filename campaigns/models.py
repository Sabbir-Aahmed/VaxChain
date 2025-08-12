from django.db import models
from users.models import DoctorProfile

class VaccineCampaign(models.Model):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    UPCOMING = 'UPCOMING'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (UPCOMING, 'Upcoming'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    vaccine_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    dosage_interval_days = models.PositiveIntegerField(default=28)
    max_participants = models.PositiveIntegerField()
    created_by = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=UPCOMING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.vaccine_type}) - {self.status}"


class VaccineSchedule(models.Model):
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    available_slots = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.campaign.name} - {self.date} ({self.start_time} - {self.end_time})"