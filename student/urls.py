from django.urls import path, re_path
from student import views


urlpatterns = [
    re_path(r'^$', views.main_pg, name='student_main_pg'),
]
