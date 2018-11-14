from django.db import models

from repository.models import UserProfile, Customer
# Create your models here.


# 学员账户同时关联CRM账户表中和客户信息表中
class Account(models.Model):
    account = models.OneToOneField(UserProfile, related_name="stu_account", on_delete=models.CASCADE)
    profile = models.OneToOneField(Customer, on_delete=models.CASCADE)
