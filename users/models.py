from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from .managers import CustomUserManager
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
    
    username = None
    email = models.EmailField(unique=True)
    nid = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(10)])
    role = models.CharField(max_length=10, choices=Role.choices)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_image = CloudinaryField( blank=True, default='default_yfddo9')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nid', 'role']

    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.email} - {self.role}"
    

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    hospital = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
    
