from django.contrib import admin
from student import models
# Register your models here.
print("student")  # 这里会在Django启动的时候执行

admin.site.register(models.Account)
