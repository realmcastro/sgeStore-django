from django.db import models
import uuid
from django.contrib.auth.models import User

class Products(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unisex'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    quantity = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=255, unique=True, blank=True, null=True)
    qr_code_generated = models.BooleanField(default=False)
    qr_code_creation_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name