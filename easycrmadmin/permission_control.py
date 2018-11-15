# 对django的权限管理了解觉得不好满足本项目的需要,所以单独写一个权限模块
# 参考https://django-guardian.readthedocs.io/en/stable/userguide/assign.html这篇
# 分配给对象级别的权限
# 动态授权,既每个用户登陆验证通过后,使用django-guardian这个第三方库来完善这个权限
#_*_coding:utf-8_*_
from easycrmadmin import models
from repository import models as r_m
# from guardian.shortcuts import assign_perm
# task = models.TaskControl.objects.create()  # 只需要实例化一次
# assign_perm('xxx', 'usr_obj', task)  # xxx表示TaskControl中Meta下的Permissions中的权限集合
# 每个用户登陆时先从数据库找到自己所拥有的权限集合,获得的集合跟TaskControl中Meta去比较, 有的就通过assign_perm进行动态授权,创建UserInfo下的
# Meta Permission元祖
# 注意要在settings中INSTALL_APP中添加'guardian'
from guardian.shortcuts import assign_perm


# def __new__(cls, *args, **kwargs):
#     return models.Model.__new__(cls)


# class DynamicPermission(models.Model):
#     class Meta:
#         permissions: (
#             ('p1', '2'), ('p2', '4')
#         )


def init_permissions(u_obj):
    """
    给验证过的用户分配权限
    :param u_obj:
    :return:
    """
    # permissions = (
    #     ('easyadmin_customers', '可以访问 客户库'),
    #     ('easyadmin_table_list', '可以访问 easyadmin 每个表的数据列表页'),
    #     ('easyadmin_table_index', '可以访问 easyadmin 首页'),
    #     ('easyadmin_table_list_view', '可以访问 easyadmin 每个表中对象的修改页'),
    #     ('easyadmin_table_list_change', '可以修改 easyadmin 每个表中对象'),
    #     ('easyadmin_table_list_action', '可以操作 每个表的 action 功能'),
    #     ('easyadmin_can_access_my_clients', '可以访问 自己的 客户列表'),
    #
    # )
    db_pms = u_obj.permissions.all()
    # print("init_permissions:", db_pms)
    for index in db_pms:  # 获得权限名称
        print(index.permission_name)
        # assign_perm('repository.view_text', u_obj)

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


from guardian.shortcuts import assign_perm
from easycrmadmin.models import BasePermission

#
# task = BasePermission.objects.create()
# joe = r_m.UserProfile.objects.get(id=7)
# print("task:", task)
# print("joe:", joe)
# assign_perm('view_task', joe, task)
# print(joe.has_perm('view_task', task))

from django.urls import resolve
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render,redirect,HttpResponse
from easycrmadmin.permission_list import perm_dic
from django.conf import settings


def perm_check(*args,**kwargs):

    request = args[0]
    resolve_url_obj = resolve(request.path)
    current_url_name = resolve_url_obj.url_name  # 当前url的url_name
    print('---perm:',request.user,request.user.is_authenticated(),current_url_name)
    #match_flag = False
    match_key = None
    match_results = [False,] #后面会覆盖，加个False是为了让all(match_results)不出错
    if request.user.is_authenticated() is False:
         return redirect(settings.LOGIN_URL)


    for permission_key,permission_val in  perm_dic.items():

        per_url_name = permission_val[0]
        per_method  = permission_val[1]
        perm_args = permission_val[2]
        perm_kwargs = permission_val[3]
        custom_perm_func = None if len(permission_val) == 4 else permission_val[4]

        if per_url_name == current_url_name: #matches current request url
            if per_method == request.method: #matches request method

                #逐个匹配参数，看每个参数时候都能对应的上。
                args_matched = False #for args only
                for item in perm_args:
                    request_method_func = getattr(request,per_method)
                    if request_method_func.get(item,None):# request字典中有此参数
                        args_matched = True
                    else:
                        print("arg not match......")
                        args_matched = False
                        break  # 有一个参数不能匹配成功，则判定为假，退出该循环。
                else:
                    args_matched = True
                #匹配有特定值的参数
                kwargs_matched = False
                for k,v in perm_kwargs.items():
                    request_method_func = getattr(request, per_method)
                    arg_val = request_method_func.get(k, None)  # request字典中有此参数
                    print("perm kwargs check:",arg_val,type(arg_val),v,type(v))
                    if arg_val == str(v): #匹配上了特定的参数 及对应的 参数值， 比如，需要request 对象里必须有一个叫 user_id=3的参数
                        kwargs_matched = True
                    else:
                        kwargs_matched = False
                        break # 有一个参数不能匹配成功，则判定为假，退出该循环。
                else:
                    kwargs_matched = True

                #自定义权限钩子
                perm_func_matched = False
                if custom_perm_func:
                    if  custom_perm_func(request,args,kwargs):
                        perm_func_matched = True
                    else:
                        perm_func_matched = False #使整条权限失效

                else: #没有定义权限钩子，所以默认通过
                    perm_func_matched = True

                match_results = [args_matched,kwargs_matched,perm_func_matched]
                print("--->match_results ", match_results)
                if all(match_results): #都匹配上了
                    match_key = permission_key
                    break

    if all(match_results):  # 全都是True
        app_name, *per_name = match_key.split('_')
        print("--->matched ",match_results,match_key)
        print(app_name, *per_name)
        perm_obj = '%s.%s' % (app_name,match_key)
        print("perm str:",perm_obj)
        if request.user.has_perm(perm_obj):
            print('当前用户有此权限')
            return True
        else:
            print('当前用户没有该权限')
            return False

    else:
        print("未匹配到权限项，当前用户无权限")


def check_permission(func):
    def inner(*args,**kwargs):
        if not perm_check(*args,**kwargs):
            request = args[0]
            return render(request,'kingadmin/page_403.html')
        return func(*args,**kwargs)
    return  inner
