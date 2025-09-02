from django.db import models


class contactd(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=500)
    message = models.CharField(max_length=2000)
# Create your models here.

class queryd(models.Model):
    name = models.CharField(max_length=100)
    message = models.CharField(max_length=2000)