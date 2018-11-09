# Create your models here.
from django.db import models

from repository.models import UserProfile, Customer
# Create your models here.


class Account(models.Model):
    account = models.OneToOneField(UserProfile, related_name="stu_account", on_delete=models.CASCADE)
    profile = models.OneToOneField(Customer, on_delete=models.CASCADE)
