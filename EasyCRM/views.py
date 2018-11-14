from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login as Login, logout as Logout
from repository import models
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, AbstractBaseUser


def login(request):
    """登陆验证"""
    errors = ""
    error_info = {}
    if request.method == "POST":
        print(request.POST.get('username'))
        print(request.POST.get('password'))
        # print(request.POST.get('choice'))  # on 或者 None
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("password:", password)

        # user = authenticate(username=username, password=password)  # 目前的Django版本无法明文比较了,这个方法不能用,超级账户除外
        # print("uiser:", user)
        try:
            user = models.UserProfile.objects.get(name=username)
            print("user", user)
            pwd = user.password
            print("pwd:", pwd)
            if user:
                if password == pwd:
                    if user.is_active:
                        Login(request, user)
                        # 这里加一个角色判断,然后跳转到对应的URL
                        print("ok")
                        print(request.GET.get("next"))
                        if request.GET.get("next") == "/easycrmadmin/":
                            print("管理员路径")
                            if user.is_admin:
                                print("是管理员")
                                return redirect(request.GET.get("next"))
                            else:
                                errors = "账户或密码错误"
                        else:
                            return redirect(request.GET.get("next"))
                        # return redirect('/market')  # 测试登陆验证用
                    else:
                        errors = "账户未激活"
                else:
                    errors = "密码错误"
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
    return redirect(reverse('mlogin'))


def get_user(self, user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


# 直接渲染,没什么动态加入的数据
class HomePageNavigation(TemplateView):
    template_name = "HomeNavPage.html"
