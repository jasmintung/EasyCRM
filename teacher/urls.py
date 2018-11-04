from django.urls import path, re_path
from teacher import views


urlpatterns = [
    re_path(r'^$', views.main_pg, name='teacher_main_pg'),
]
