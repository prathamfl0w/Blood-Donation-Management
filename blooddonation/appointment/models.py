from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

class Appointment(models.Model):
    APPOINTMENT_TYPES = [
        ('Donation', 'Blood Donation'),
        ('Checkup', 'Medical Checkup'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    message = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    duration = models.DurationField(default=timedelta(hours=1))

    def __str__(self):
        return f"{self.full_name} - {self.type} on {self.date}"

