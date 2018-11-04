from django.contrib import admin
from easycrmadmin import models

# Register your models here.
print("easycrmadmin")  # 这里会在Django启动的时候执行


# 注册,Django Admin登陆时能看到这些表
admin.site.register(models.Customer)
admin.site.register(models.UserProfile)
admin.site.register(models.Course)
admin.site.register(models.ClassList)
admin.site.register(models.StudyRecord)
admin.site.register(models.StuAccount)
admin.site.register(models.Role)
admin.site.register(models.CourseRecord)
admin.site.register(models.Branch)
admin.site.register(models.Enrollment)
admin.site.register(models.Menu)
admin.site.register(models.PaymentRecord)
admin.site.register(models.CustomerFollowUp)
