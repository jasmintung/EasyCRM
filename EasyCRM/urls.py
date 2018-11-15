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
from django.urls import path, re_path
from django.conf.urls import include
from EasyCRM import views
from EasyCRM import views
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('accounts/login/', views.login, name="mlogin"),  # 没有登陆时Django会自动走到这里进行登陆验证
    re_path('accounts/logout/', views.logout, name="mlogout"),
    path('easycrmadmin/', include('easycrmadmin.urls')),
    path('market/', include('market.urls')),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
    path('boss/', include('boss.urls')),
    path('', cache_page(60*60*24)(views.HomePageNavigation.as_view())),  # 主页一天刷新一次缓存
]
