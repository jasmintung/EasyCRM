from easycrmadmin.easycrm_admin import BaseEasyCrmAdmin, site
from django.shortcuts import HttpResponse
from repository import models


class CourseRecordAdmin(BaseEasyCrmAdmin):
    list_display = ('from_class', 'day_num', 'teacher', 'has_homework', 'homework_title', 'homework_requirement', )
    list_filter = ['from_class']
    actions = ['initialize_studyrecords']

    def initialize_studyrecords(self, request, queryset):
        print("initialize_courserecords")
        # print(queryset[0])  # CourseRecord对象
        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():  # 反向查询得到报名记录
            new_obj_list.append(models.StudyRecord(student=enroll_obj, course_record=queryset[0], attendance=0,
                                                   score=0))

        try:
            print("课程记录:", new_obj_list)
            models.StudyRecord.objects.bulk_create(new_obj_list)  # 批量创建
            return HttpResponse("操作成功")
        except Exception as e:
            return HttpResponse("批量初始化失败")
    initialize_studyrecords.short_description = "初始化上课记录"


class StudyRecordAdmin(BaseEasyCrmAdmin):
    list_display = ['student', 'course_record', 'attendance', 'score', 'date']
    list_filter = ['course_record', 'score', 'attendance']
    list_editable = ['score', 'attendance']


site.register(models.CourseRecord, CourseRecordAdmin)
site.register(models.StudyRecord, StudyRecordAdmin)
