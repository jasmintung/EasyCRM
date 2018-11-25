from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login as Login, logout as Logout
from repository import models
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, AbstractBaseUser
from easycrmadmin import permission_control


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


        try:
            users = authenticate(username=username, password=password)
            print("uiser:", users)
            if users:
                if users.is_active:
                    users.backend = 'django.contrib.auth.backends.ModelBackend'
                    Login(request, users)
                    # 这里加一个角色判断,然后跳转到对应的URL
                    print("ok")
                    print(request.GET.get("next"))
                    if request.GET.get("next") == "/easycrmadmin/":
                        print("管理员路径")
                        if users.is_admin:
                            print("是管理员")
                            return redirect(request.GET.get("next"))
                        else:
                            errors = "账户或密码错误"
                    else:
                        # 动态分配权限,保留功能,未开发
                        role = request.GET.get("next")
                        print("user obj:", id(request.user), id(users))  # 是同一个引用,所以随便传哪个都行,很好!!
                        permission_control.init_permissions(users, role.strip('/'))
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
    Logout(request)
    print("logout.....")
    return redirect('/')


def get_user(self, user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


# 直接渲染,没什么动态加入的数据
class HomePageNavigation(TemplateView):
    template_name = "HomeNavPage.html"
