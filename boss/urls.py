from django.urls import path, re_path
from boss import views


urlpatterns = [
    re_path(r'^$', views.main_pg, name='boss_main_pg'),
]
