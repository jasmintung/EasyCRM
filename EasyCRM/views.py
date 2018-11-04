from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as Login, logout as Logout


def login(request):
    """登陆验证"""
    if request.method == "POST":
        print(request.POST.get('username'))
        print(request.POST.get('password'))
        print(request.POST.get('choice'))  # on 或者 None
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            print(type(user))
            print(user)
            Login(request, user)
            # 这里加一个角色判断,然后跳转到对应的URL
            return redirect('/easycrmadmin')  # 测试登陆验证用
            # return redirect('/market')  # 测试登陆验证用
    return render(request, 'login.html')


def logout(request):
    return redirect('/login')
