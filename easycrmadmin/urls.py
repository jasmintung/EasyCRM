from django.urls import path, re_path
from easycrmadmin import views


urlpatterns = [
    path('', views.main_pg, name='easy_admin_main_pg'),  # 所有APP及所有的表
    re_path(r'^(\w+)/$', views.app_tables, name='app_tables'),  # APP里所有的表
    re_path(r'^(\w+)/(\w+)/$', views.table_display, name='this_table'),  # 当前表
    re_path(r'^(\w+)/(\w+)/add/$', views.table_add, name='table_add'),  # 创建表
    re_path(r'^(\w+)/(\w+)/modify/(\d+)/$', views.table_modify, name='table_modify'),  # 修改表
    re_path(r'^(\w+)/(\w+)/delete/(\d+)/$', views.table_delete, name='table_delete'),  # 删除

    # re_path(r'^login/$', views.login, name='login'),
    # re_path(r'^logout/$', views.logout, name='logout'),
]
