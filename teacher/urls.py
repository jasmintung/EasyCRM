from django.urls import path, re_path
from teacher import views


urlpatterns = [
    re_path(r'^$', views.main_pg, name='teacher_main_pg'),
    re_path(r'^my_classes/$', views.my_classes, name='my_classes'),
    re_path(r'^my_classes/(\w+)/(\w+)/(\d+)/$', views.course_record_display, name='course_record'),
    re_path(r'^my_classes/(\d+)/stu_list/$', views.view_class_stu_list, name='view_class_stu_list'),
]
