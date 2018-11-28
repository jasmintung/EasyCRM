from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from repository import models
from easycrmadmin import views as easy_admin_views
from easycrmadmin.easycrm_admin import site
from easycrmadmin import permission_control
from django.contrib.auth.models import Permission
# Create your views here.


had_allote_permission = False


def allote_market_permissions(request):
    if Permission.objects.get(codename='this_table'):
        perm_obj = Permission.objects.get(codename='this_table')
        request.user.user_permissions.add(perm_obj)
    if Permission.objects.get(codename='table_modify'):
        perm_obj = Permission.objects.get(codename='table_modify')
        request.user.user_permissions.add(perm_obj)
    if Permission.objects.get(codename='table_add'):
        perm_obj = Permission.objects.get(codename='table_add')
        request.user.user_permissions.add(perm_obj)
    # if Permission.objects.get(codename='table_delete'):
    #     perm_obj = Permission.objects.get(codename='table_add')
    #     request.user.user_permissions.add(perm_obj)

    global had_allote_permission
    had_allote_permission = True


@login_required
@permission_control.check_permission
def main_pg(request):
    print('teacher')
    if had_allote_permission is False:
        allote_market_permissions(request)
    return render(request, 'teacher/teacher_main_pg.html')


@login_required
@permission_control.check_permission
def view_class_stu_list(request, cid):
    class_obj = models.ClassList.objects.get(id=cid)
    print("class_obj:", class_obj)
    return render(request, 'teacher/class_stu_list.html', {'class_obj': class_obj})


@login_required
@permission_control.check_permission
def my_classes(request):
    return render(request, 'teacher/my_classes.html')


@login_required
@permission_control.check_permission
def course_record_display(request, app_name, model_name, cr_id):
    """
    上课记录处理
    :param request:
    :param app_name: APP
    :param model_name: 上课记录表名
    :param cr_id: 班级ID
    :return:
    """
    print(app_name, model_name, cr_id)
    tp_data = easy_admin_views.table_display(request, 'repository', 'courserecord', innercall=True)
    # print("tp:", tp_data)
    tp_data['class_id'] = cr_id
    return render(request, 'teacher/course_record_display.html', tp_data)
