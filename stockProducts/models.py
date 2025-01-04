from django.db import models
import uuid
from django.conf import settings

class Products(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unisex'),
    ]

    id = models.AutoField(primary_key=True)
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
    

class StockHistory(models.Model):

    product = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=20)
    field_changed = models.CharField(max_length=50, blank=True, null=True)
    old_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)
    old_quantity = models.IntegerField(null=True, blank=True)
    new_quantity = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.get_action_display()} - {self.product.name} - {self.date}"

    class Meta:
        ordering = ['-date']