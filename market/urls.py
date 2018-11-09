from django.urls import path, re_path
from market import views


urlpatterns = [
    re_path(r'^$', views.main_pg, name='market_main_pg'),
    re_path(r'^customers/$', views.customers, name='customers'),
    re_path(r'^customers/modify/(\d+)/$', views.customers_modify, name='customer_modify'),
    re_path(r'^enrollment/(\d+)/$', views.enrollment, name='enrollment'),
    re_path(r'^enrollment/stu/(\d+)/$', views.stu_enrollment, name='stu_enrollment')
]
