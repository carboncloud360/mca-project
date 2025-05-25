from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

SERVICE_CHOICES = (
    ("Consultation with a Cardiologist", "Consultation with a Cardiologist"),
    ("Cardiac Diagnostic Testing", "Cardiac Diagnostic Testing"),
    ("Stress Testing", "Stress Testing"),
    ("Cardiac Imaging", "Cardiac Imaging"),
    ("Cardiac Rehabilitation Program", "Cardiac Rehabilitation Program"),
)
TIME_CHOICES = (
    ("9 AM", "9 AM"),
    ("10 AM", "10 AM"),
    ("11 AM", "11 AM"),
    ("12 PM", "12 PM"),
    ("1 PM", "1 PM"),
    ("2 PM", "2 PM"),
    ("3 PM", "3 PM"),
    ("4 PM", "4 PM"),
    ("5 PM", "5 PM"),
    ("6 PM", "6 PM"),
    ("7 PM", "7 PM"),
)


class Appointment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    service = models.CharField(
        max_length=50, choices=SERVICE_CHOICES, default="Consultation with a Cardiologist")
    day = models.DateField(default=datetime.now)
    time = models.CharField(
        max_length=10, choices=TIME_CHOICES, default="9 AM")
    time_ordered = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"{self.user.username} | day: {self.day} | time: {self.time}"
