
from django.db import models

class CustomUser(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=80)
    date_added = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
