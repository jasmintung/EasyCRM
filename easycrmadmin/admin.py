from django.contrib import admin
from repository import models
from django.shortcuts import HttpResponse
# from easycrmadmin import models as as_models
# Register your models here.
print("easycrmadmin")  # 这里会在Django启动的时候执行


def initialize_permissions(modeladmin, request, queryset):
    print("initialize_permissions")

    try:
        # models.StudyRecord.objects.bulk_create(new_obj_list)
        return HttpResponse("操作成功")
    except Exception as e:
        return HttpResponse("批量初始化失败")


initialize_permissions.short_description = "批量初始化权限"


class TaskPermissionAdmin(admin.ModelAdmin):
    actions = ['initialize_permissions']


# 注册,Django Admin登陆时能看到这些表
# admin.site.register(models.Customer)
# admin.site.register(models.UserProfile)
# admin.site.register(models.Course)
# admin.site.register(models.ClassList)
# admin.site.register(models.StudyRecord)
# admin.site.register(models.StuAccount)
# admin.site.register(models.Role)
# admin.site.register(models.CourseRecord)
# admin.site.register(models.Branch)
# admin.site.register(models.Enrollment)
# admin.site.register(models.Menu)
# admin.site.register(models.PaymentRecord)
# admin.site.register(models.CustomerFollowUp)
admin.site.register(models.ContractTemplate)
admin.site.register(models.AdminPermission)
admin.site.register(models.SalesPermission)
admin.site.register(models.TeacherPermission)
admin.site.register(models.StudentPermission)
# admin.site.register(as_models.TaskControl)
# admin.site.register(as_models.BasePermission)
