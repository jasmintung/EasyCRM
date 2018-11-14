from django.urls import path, re_path
from student import views


urlpatterns = [
    re_path(r'^$', views.my_courses, name='my_courses'),
    re_path(r'my_grade/$', views.my_grade, name='my_grade'),
    re_path(r'course/(\d+)/homework/(\d+)/$', views.my_homework_detail, name="homework_detail"),
    re_path(r'course/(\d+)/homework/(\d+)/delete/$', views.delete_file, name='delete_file'),
    re_path(r'course/(\d+)/homework/$', views.my_homeworks, name='my_homeworks'),
]
