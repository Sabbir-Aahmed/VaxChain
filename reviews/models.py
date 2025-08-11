from django.db import models
from django.conf import settings
from campaigns.models import VaccineCampaign
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'})
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name='review')
    ratings = models.PositiveBigIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'campaign')

    def __str__(self):
        return f"Review {self.ratings} by {self.patient.first_name} on {self.campaign.name}"