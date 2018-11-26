# 对django的权限管理了解觉得不好满足本项目的需要,所以单独写一个权限模块
# 参考https://django-guardian.readthedocs.io/en/stable/userguide/assign.html这篇
# 分配给对象级别的权限
# 动态授权,既每个用户登陆验证通过后,使用django-guardian这个第三方库来完善这个权限
# -*- coding:utf-8 -*-
from repository import models
from django.http import Http404
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
# assign_perm('xxx', 'usr_obj', task)  # xxx表示TaskControl中Meta下的Permissions中的权限集合
# 每个用户登陆时先从数据库找到自己所拥有的权限集合,获得的集合跟TaskControl中Meta去比较, 有的就通过assign_perm进行动态授权,创建UserInfo下的
# Meta Permission元祖
# 注意要在settings中INSTALL_APP中添加'guardian'
from guardian.shortcuts import assign_perm
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms


# def __new__(cls, *args, **kwargs):
#     return models.Model.__new__(cls)


# class DynamicPermission(models.Model):
#     class Meta:
#         permissions: (
#             ('p1', '2'), ('p2', '4')
#         )
# class PermissionAdmin(object):
#     def __init__(self, user_obj, ):


def init_permissions(u_obj, role):
    """
    给验证过的用户分配权限,因该是管理员对其进行批量分配,先这样用吧,
    :param u_obj:
    :param role: 登陆角色
    :return:
    """
    print("init_permission:", role)
    if u_obj.is_admin:
        if role == "easycrmadmin":

            # ad_gp = Group.objects.get(name='管理员组')
            # print("ad_gp:", id(ad_gp))
            pm = models.AdminPermission.objects.first()  # 获取权限对象
            # print(pm._meta.permissions)
            pm_l = (index[0] for index in pm._meta.permissions)
            return pm_l
            # for i in pm_l:
            #     print(i)
            # print(pm.Meta)
            # if pm not in permissions_list:
            #     print("pm:", pm)
            #     permissions_list.append(pm)

            # print(dir(pm))
            # print("-----------------------")
            # u_obj.user_permissions.clear()
            # remove_perm('easy_admin_main_pg', u_obj, pm)
            # remove_perm('app_tables', u_obj, pm)
            # remove_perm('this_table', u_obj, pm)
            # remove_perm('table_add', u_obj, pm)
            # remove_perm('table_modify', u_obj, pm)
            # remove_perm('table_delete', u_obj, pm)
            # print(u_obj.has_perm('easy_admin_main_pg', pm))
            # if not u_obj.has_perm('easy_admin_main_pg', pm):
            #     print("gogogogogogogo")
            #     assign_perm('easy_admin_main_pg', u_obj, pm)
            # if not u_obj.has_perm('app_tables', pm):
            #     assign_perm('app_tables', u_obj, pm)
            # if not u_obj.has_perm('this_table', pm):
            #     assign_perm('this_table', u_obj, pm)
            # if not u_obj.has_perm('table_add', pm):
            #     assign_perm('table_add', u_obj, pm)
            # if not u_obj.has_perm('table_modify', pm):
            #     assign_perm('table_modify', u_obj, pm)
            # if not u_obj.has_perm('table_delete', pm):
            #     assign_perm('table_delete', u_obj, pm)
            # u_obj.groups.add(ad_gp)
            # print(u_obj.name)
            # print(u_obj.has_perm('easy_admin_main_pg', pm))
    else:
        if role == "market":
            sale_gp = Group.objects.get(name='销售组')
            print("sale_gp:", sale_gp)
            pm = models.SalesPermission.objects.first()  # 获取权限对象
            # if pm not in permissions_list:
            #     permissions_list.append(pm)
            print("pm:", pm)
            # print(dir(pm))
            # print("-----------------------")
            # print(u_obj.has_perm('market_main_pg', pm))
            # if not u_obj.has_perm('market_main_pa', pm):
            #     assign_perm('market_main_pg', sale_gp, pm)
            # if not u_obj.has_perm('customers', pm):
            #     assign_perm('customers', sale_gp, pm)
            # if not u_obj.has_perm('customer_modify', pm):
            #     assign_perm('customer_modify', sale_gp, pm)
            # if not u_obj.has_perm('enrollment', pm):
            #     assign_perm('enrollment', sale_gp, pm)
            # if not u_obj.has_perm('stu_enrollment', pm):
            #     assign_perm('stu_enrollment', sale_gp, pm)
            # u_obj.groups.add(sale_gp)
        elif role == "teacher":
            tc_gp = Group.objects.get(name='讲师组')
            print("tc_gp:", tc_gp)
            pm = models.TeacherPermission.objects.first()  # 获取权限对象
            # if pm not in permissions_list:
            #     permissions_list.append(pm)
            print("pm:", pm)
            # print(dir(pm))
            # print("-----------------------")
            # if not u_obj.has_perm('teacher_main_pg', pm):
            #     assign_perm('teacher_main_pg', tc_gp, pm)
            # if not u_obj.has_perm('my_classes', pm):
            #     assign_perm('my_classes', tc_gp, pm)
            # if not u_obj.has_perm('course_record', pm):
            #     assign_perm('course_record', tc_gp, pm)
            # if not u_obj.has_perm('view_class_stu_list', pm):
            #     assign_perm('view_class_stu_list', tc_gp, pm)
            # u_obj.groups.add(tc_gp)
        elif role == "student":
            st_gp = Group.objects.get(name='学员组')
            print("st_gp:", st_gp)
            pm = models.StudentPermission.objects.first()  # 获取权限对象
            print("pm:", pm)
            # if pm not in permissions_list:
            #     permissions_list.append(pm)
            # print(dir(pm))
            # print("-----------------------")
            # if not u_obj.has_perm('my_courses', pm):
            #     assign_perm('my_courses', st_gp, pm)
            # if not u_obj.has_perm('my_grade', pm):
            #     assign_perm('my_grade', st_gp, pm)
            # if not u_obj.has_perm('homework_detail', pm):
            #     assign_perm('homework_detail', st_gp, pm)
            # if not u_obj.has_perm('delete_file', pm):
            #     assign_perm('delete_file', st_gp, pm)
            # if not u_obj.has_perm('my_homeworks', pm):
            #     assign_perm('my_homeworks', st_gp, pm)
            # u_obj.groups.add(st_gp)
        else:
            pass
    # db_pms = u_obj.permissions.all()
    # # print("init_permissions:", db_pms)
    # for index in db_pms:  # 获得权限名称
    #     print(index.permission_name)
    #     # assign_perm('repository.view_text', u_obj)

    # print(dir(pr_obj))
    # print(dir(u_obj))
    # permissions = (('p1', '2'), ('p2', '4'))
    # pr_obj.Meta = permissions
    # print(pr_obj.Meta)
    # print(pr_obj.Meta.permissions)
    # u_obj.Meta.permissions = ('p1', 2) ok

    # print(dir(u_obj))
    # print(u_obj.Meta.permissions)
    # class Meta:
    #     pass
    #
    # setattr(Meta, 'permissions', (('p1', '2'), ('p2', '4')))
    # attrs = {'Meta': Meta}
    #
    # DynamicPermission = type("DynamicPermission", (models.BasePermission,), attrs)
    # xiaohuamao = DynamicPermission()
    # print(dir(xiaohuamao))

#
# from guardian.shortcuts import assign_perm
# from easycrmadmin.models import BasePermission
#
# #
# # task = BasePermission.objects.create()
# # joe = r_m.UserProfile.objects.get(id=7)
# # print("task:", task)
# # print("joe:", joe)
# # assign_perm('view_task', joe, task)
# # print(joe.has_perm('view_task', task))
#

from django.urls import resolve
from django.http import Http404, HttpResponseRedirect
# from django.shortcuts import render,redirect,HttpResponse
# from easycrmadmin.permission_list import perm_dic
# from django.conf import settings
#
#


def perm_check(*args, **kwargs):
    request = args[0]
    resolve_url_obj = resolve(request.path)
    print(dir(request.user))
    # print("resolve_url_obj:", resolve_url_obj)
    current_url_name = resolve_url_obj.url_name  # 当前url的url_name
    print("current_url:", current_url_name)
    # print(permissions_list)
    # pm_list = (pm for pm in permissions_list)
    has_permission = True
    print("222:", request.user.user_permissions.values())
    return has_permission

    # print(request.user.has_perm('view_task', task))
    # current_url_name = resolve_url_obj.url_name  # 当前url的url_name
    # print('---perm:',request.user,request.user.is_authenticated(),current_url_name)
    # #match_flag = False
    # match_key = None
    # match_results = [False,] #后面会覆盖，加个False是为了让all(match_results)不出错
    # if request.user.is_authenticated() is False:
    #      return redirect(settings.LOGIN_URL)
    #
    #
    # for permission_key,permission_val in  perm_dic.items():
    #
    #     per_url_name = permission_val[0]
    #     per_method  = permission_val[1]
    #     perm_args = permission_val[2]
    #     perm_kwargs = permission_val[3]
    #     custom_perm_func = None if len(permission_val) == 4 else permission_val[4]
    #
    #     if per_url_name == current_url_name: #matches current request url
    #         if per_method == request.method: #matches request method
    #
    #             #逐个匹配参数，看每个参数时候都能对应的上。
    #             args_matched = False #for args only
    #             for item in perm_args:
    #                 request_method_func = getattr(request,per_method)
    #                 if request_method_func.get(item,None):# request字典中有此参数
    #                     args_matched = True
    #                 else:
    #                     print("arg not match......")
    #                     args_matched = False
    #                     break  # 有一个参数不能匹配成功，则判定为假，退出该循环。
    #             else:
    #                 args_matched = True
    #             #匹配有特定值的参数
    #             kwargs_matched = False
    #             for k,v in perm_kwargs.items():
    #                 request_method_func = getattr(request, per_method)
    #                 arg_val = request_method_func.get(k, None)  # request字典中有此参数
    #                 print("perm kwargs check:",arg_val,type(arg_val),v,type(v))
    #                 if arg_val == str(v): #匹配上了特定的参数 及对应的 参数值， 比如，需要request 对象里必须有一个叫 user_id=3的参数
    #                     kwargs_matched = True
    #                 else:
    #                     kwargs_matched = False
    #                     break # 有一个参数不能匹配成功，则判定为假，退出该循环。
    #             else:
    #                 kwargs_matched = True
    #
    #             #自定义权限钩子
    #             perm_func_matched = False
    #             if custom_perm_func:
    #                 if  custom_perm_func(request,args,kwargs):
    #                     perm_func_matched = True
    #                 else:
    #                     perm_func_matched = False #使整条权限失效
    #
    #             else: #没有定义权限钩子，所以默认通过
    #                 perm_func_matched = True
    #
    #             match_results = [args_matched,kwargs_matched,perm_func_matched]
    #             print("--->match_results ", match_results)
    #             if all(match_results): #都匹配上了
    #                 match_key = permission_key
    #                 break
    #
    # if all(match_results):  # 全都是True
    #     app_name, *per_name = match_key.split('_')
    #     print("--->matched ",match_results,match_key)
    #     print(app_name, *per_name)
    #     perm_obj = '%s.%s' % (app_name,match_key)
    #     print("perm str:",perm_obj)
    #     if request.user.has_perm(perm_obj):
    #         print('当前用户有此权限')
    #         return True
    #     else:
    #         print('当前用户没有该权限')
    #         return False
    #
    # else:
    #     print("未匹配到权限项，当前用户无权限")


# def check_permission(func):
#     def inner(*args,**kwargs):
#         if not perm_check(*args,**kwargs):
#             request = args[0]
#             return render(request,'kingadmin/page_403.html')
#         return func(*args,**kwargs)
#     return inner


def check_permission(func):
    def inner(*args, **kwargs):
        if not perm_check(*args, **kwargs):
            raise Http404("您没有权限访问")
        return func(*args, **kwargs)
    return inner
