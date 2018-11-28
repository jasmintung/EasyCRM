from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login as Login, logout as Logout
from repository import models
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, AbstractBaseUser
from easycrmadmin import permission_control
from django.core.exceptions import ValidationError
from forms import registe_form, login_form
from django.contrib.auth.models import Permission
from django.db import transaction
import json, time


class JsonCustomEncoder(json.JSONEncoder):
    """
    解决出现两次序列化的问题
    """
    def default(self, field):
        if isinstance(field, ValidationError):
            return {'code': field.code, 'message': field.message}
        else:
            return json.JSONEncoder.default(self, field)


def login(request):
    """登陆验证,没有手动清除cookies或者退出的话,下一次直接可访问页面程序不会执行这里"""
    errors = ""
    error_info = {}
    if request.method == "POST":
        print(request.POST.get('username'))
        print(request.POST.get('password'))
        # print(request.POST.get('choice'))  # on 或者 None
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("password:", password)

        try:
            users = authenticate(username=username, password=password)
            # print("uiser:", users)
            if users:
                if users.is_active:
                    # users.backend = 'guardian.backends.ObjectPermissionBackend' 搞不定这个,折腾了蛮久,后续有空再研究吧
                    users.backend = 'django.contrib.auth.backends.ModelBackend'
                    Login(request, users)
                    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    users.last_login = now_time  # 使用自定义用户认证后会有一个最后登陆时间字段
                    users.save()
                    role = request.GET.get("next")
                    if request.GET.get("next") == "/easycrmadmin/":
                        print("管理员路径")
                        # 这里加一个角色判断,然后跳转到对应的URL
                        if users.is_admin:
                            # t_list = []
                            print("是管理员")
                            usr_obj = models.UserProfile.objects.get(name=users.name)
                            pm_list = permission_control.init_permissions(usr_obj, role.strip('/'))
                            request.user.user_permissions.remove()
                            # 终于实现了动态分配权限, what a day!!!
                            for i in pm_list:
                                print(i)
                                # t_list.append(i)
                                if Permission.objects.get(codename=i):
                                    perm_obj = Permission.objects.get(codename=i)  # 不能出现相同的权限,因为这个方法会把所有Model下的Permissions都找到
                                else:
                                    Permission.objects.create(name=i, content_type_id=2, codename=i)
                                    perm_obj = Permission.objects.get(codename=i)
                                request.user.user_permissions.add(perm_obj)
                            print(request.user.user_permissions.values())

                            # print(request.user.user_permissions.values())
                            # if perm_obj:
                            #     request.user.user_permissions.add(perm_obj)
                            # request.user.user_permissions.add(perm_obj)
                            # for i in pm_list:
                            #     Permission.objects.create(name=i, content_type_id=2)
                            #     perm_obj = Permission.objects.get(codename=i)
                            #     request.user.user_permissions.add(perm_obj)
                            #     print(request.user.user_permissions.values())
                            # request.user.cus_pm = t_list  # 这样赋值不行的!

                            return redirect(request.GET.get("next"))
                            # return ("hello")
                        else:
                            errors = "账户或密码错误"
                    else:
                        # 非管理员的非客户对象的账户及权限由管理员进行统一创建.
                        # print("1after fenpei:", request.user.has_perm("p1"))
                        # print("2after fenpei:", request.user.has_perm("repository.p5"))
                        return redirect(request.GET.get("next"))
                        # return redirect('/market')  # 测试登陆验证用
                else:
                    errors = "账户未激活"
            else:
                errors = "账户名或密码错误"
        except models.UserProfile.DoesNotExist as ex:
            # user = User(username=username)
            # user.is_staff = True
            # user.is_superuser = True
            # user.save()
            errors = "账户不存在"
    return render(request, 'login.html', {'error_info': errors})


def logout(request):
    # request.user.user_permissions.clear()  # 删除权限,这行代码会对数据表进行操作
    print(request.user.user_permissions.values())
    Logout(request)
    print("logout.....")
    print(request.user.user_permissions.values())
    return redirect('/')


def get_user(self, user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


def register(request):
    if request.method == "GET":
        dic = {
            'email': '',
            'name': '',
            'password': '',
            'password2': '',
        }
        rg = registe_form.RGFM(dic)
        return render(request, 'register.html', {'rg_obj': rg})
    elif request.method == "POST":
        # print(request.POST)
        rg_auth_form = registe_form.RGFM(request.POST)
        if rg_auth_form.is_valid():
            print("data ok!")
            print(request.POST.get('password'))
            # 分配权限, 目前这个注册流程只对学员客户
            try:
                with transaction.atomic():
                    new_user = models.UserProfile.objects.create_user(email=request.POST.get('email'),
                                                                      name=request.POST.get('name'),
                                                                      password=request.POST.get('password'))
                    st_role_obj = models.Role.objects.get(name="学员")
                    # print(st_role_obj.id)
                    new_user.roles.add(st_role_obj)
                    # print(new_user)
                    new_user.set_password(request.POST.get('password'))  # 设置hash
                    new_user.save()
                    user_obj = models.UserProfile.objects.get(name=request.POST.get('name'))
                    # print("oooooo: ", user_obj)
                    permission_control.allot_permissions(user_obj, ['1'])
            except Exception as ex:
                return HttpResponse(ex)
            return redirect("/")
        else:
            print("not pass")
            result = rg_auth_form.errors
            return render(request, 'register.html', {'rg_obj': rg_auth_form, 'errors': result})


# 直接渲染,没什么动态加入的数据
class HomePageNavigation(TemplateView):
    template_name = "HomeNavPage.html"
