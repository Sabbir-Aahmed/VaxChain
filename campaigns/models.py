from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

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
    campaign_image = CloudinaryField( blank=True, default='vaxCamp_tqt2sl')
    vaccine_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    dosage_interval_days = models.PositiveIntegerField(default=28)
    max_participants = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
        return f"Schedule {self.id} on {self.date}"