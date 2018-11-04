"""EasyCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from EasyCRM import views
# from easycrmadmin import urls
# from market import urls
# from student import urls
# from teacher import urls
# from boss import urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('login/', views.logout),
    path('easycrmadmin/', include('easycrmadmin.urls')),
    path('market/', include('market.urls')),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
    path('boss/', include('boss.urls')),
]
