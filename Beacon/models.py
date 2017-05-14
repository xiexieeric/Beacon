from django.contrib.auth.models import User
from django.db import models

class UserWrapper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=15)
    tel = models.CharField(max_length=15)



class Listing(models.Model):
    poster = models.ForeignKey(User, related_name="poster")
    matches = models.ForeignKey(User, blank=True)
    lat = models.CharField(max_length=30)
    lon = models.CharField(max_length=30)
    leavingTime = models.DateTimeField()