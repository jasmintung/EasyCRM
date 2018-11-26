from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login as Login, logout as Logout
from repository import models
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, AbstractBaseUser
from easycrmadmin import permission_control
from django.core.exceptions import ValidationError
from forms import registe_form
from django.contrib.auth.models import Permission
import json


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
            print(users.backend)
            if users:
                if users.is_active:
                    # users.backend = 'guardian.backends.ObjectPermissionBackend' 搞不定这个,折腾了蛮久,后续有空再研究吧
                    users.backend = 'django.contrib.auth.backends.ModelBackend'
                    Login(request, users)
                    # 这里加一个角色判断,然后跳转到对应的URL
                    # print("ok")
                    # print(request.GET.get("next"))
                    role = request.GET.get("next")
                    if request.GET.get("next") == "/easycrmadmin/":
                        print("管理员路径")
                        if users.is_admin:
                            t_list = []
                            print("是管理员")
                            usr_obj = models.UserProfile.objects.get(name=users.name)
                            pm_list = permission_control.init_permissions(usr_obj, role.strip('/'))
                            # 终于实现了动态分配权限, what a day!!!
                            for i in pm_list:
                                print(i)
                                t_list.append(i)
                            if Permission.objects.get(codename="fb book"):
                                perm_obj = Permission.objects.get(codename="fb book")
                            else:
                                Permission.objects.create(name="fb book", content_type_id=2, codename="fb book")
                                perm_obj = Permission.objects.get(codename="fb book")
                            request.user.user_permissions.add(perm_obj)
                            print(request.user.user_permissions.values())
                            print(request.user.user_permissions.remove())
                            print(request.user.user_permissions.values())
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
                        # 动态分配权限
                        permission_control.init_permissions(users, role.strip('/'))
                        print("user obj:", id(request.user), id(users))  # 是同一个引用,所以随便传哪个都行,很好!!

                        # print("1after fenpei:", request.user.has_perm("p1"))
                        # print("2after fenpei:", request.user.has_perm("repository.p5"))
                        #  return redirect(request.GET.get("next"))
                        # return HttpResponseRedirect("/")
                        return redirect('/market')  # 测试登陆验证用
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
        msg = ""
        print(request.POST)
        rg_auth_form = registe_form.RGFM(request.POST)
        if rg_auth_form.is_valid():
            print("data ok!")
            return HttpResponse("注册成功,可以正常访问了")
        else:
            print("not pass")
            result = rg_auth_form.errors
            return render(request, 'register.html', {'rg_obj': rg_auth_form, 'errors': result})


# 直接渲染,没什么动态加入的数据
class HomePageNavigation(TemplateView):
    template_name = "HomeNavPage.html"

