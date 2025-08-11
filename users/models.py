from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from .managers import CustomUserManager

class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
    
    username = None
    email = models.EmailField(unique=True)
    nid = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(10)])
    role = models.CharField(max_length=10, choices=Role.choices)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles", blank=True, default="profiles/default.jpg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nid', 'role']

    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.email} - {self.role}"
    
    
