from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.contrib.auth import get_user_model

# core/models.py

SECURITY_QUESTIONS = [
    ("pet_name", "What is your pet’s name?"),
    ("birth_city", "In what city were you born?"),
    ("first_school", "What is the name of your first school?")
]
# Create your models here.
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
]

def get_default_user():
    User = get_user_model()
    return User.objects.first().id if User.objects.exists() else None

class CustomUser(AbstractUser):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    phone = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)  
    city = models.CharField(max_length=100)
    security_question = models.CharField(max_length=50, choices=SECURITY_QUESTIONS, blank=True)
    security_answer = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

class Donor(models.Model):
    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('pending', 'Pending Verification')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    availability_status = models.CharField(
        max_length=20, 
        choices=AVAILABILITY_STATUS, 
        default='pending'
    )
    medical_history = models.TextField(blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    registered_date = models.DateField(default=timezone.now)  # Changed from auto_now_add

    def __str__(self):
        return f"{self.user.username} - {self.blood_group} ({self.availability_status})"

    def update_availability(self):
        if self.last_donation_date:
            days_since_donation = (timezone.now().date() - self.last_donation_date).days
            self.is_available = days_since_donation >= 56
            self.save()

    class Meta:
        ordering = ['-registered_date']
        verbose_name = 'Donor'
        verbose_name_plural = 'Donors'

class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=get_default_user
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    hospital_name = models.CharField(max_length=100, default='')
    hospital_address = models.TextField(default='')
    contact_name = models.CharField(max_length=100, default='')
    contact_number = models.CharField(max_length=15, default='')
    urgency = models.CharField(max_length=8, choices=URGENCY_CHOICES, default='medium')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    additional_notes = models.TextField(blank=True, default='')
    requester_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contact_name} - {self.blood_group} ({self.status})"

class Donation(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_TYPES)
    amount_ml = models.PositiveIntegerField()  # Donation in milliliters
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed')

    def __str__(self):
        return f"{self.donor.username} - {self.blood_group} - {self.amount_ml}ml"

class DonorDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    amount_ml = models.PositiveIntegerField(default=450)
    donation_date = models.DateField(auto_now_add=True)
    medical_conditions = models.TextField(blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.donor.user.username} - {self.blood_group} - {self.amount_ml}ml - {self.status}"

    class Meta:
        ordering = ['-donation_date']
        verbose_name = 'Donor Donation'
        verbose_name_plural = 'Donor Donations'



