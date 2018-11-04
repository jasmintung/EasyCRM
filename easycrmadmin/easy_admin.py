from easycrmadmin import models
from easycrmadmin.easycrm_admin import BaseEasyCrmAdmin, site


class CustomerAdmin(BaseEasyCrmAdmin):
    list_display = ('id', 'name', 'qq', 'consultant', 'source', 'status', 'date')  # 允许显示的字段
    list_filter = ('source', 'status', 'consultant')  # 允许过滤的字段
    search_fields = ('qq', 'name', 'status')
    list_editable = ('status', 'phone', 'source')
    list_per_page = 5
    readonly_fields = ('name',)
    actions = ["change_status"]

    def change_status(self, request, querysets):
        print("changeing status", querysets)
        querysets.update(status=1)

    change_status.short_description = "改变报名状态"


class CourseAdmin(BaseEasyCrmAdmin):
    list_display = ('name', 'outline', 'price')


class ClassListAdmin(BaseEasyCrmAdmin):
    list_display = ('course', 'semester')


site.register(models.Customer, CustomerAdmin)
site.register(models.ClassList, ClassListAdmin)
site.register(models.CourseRecord)
site.register(models.Course, CourseAdmin)
