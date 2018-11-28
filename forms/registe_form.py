import re
from django import forms
from django.forms import fields
from django.forms import widgets
from repository.models import UserProfile
from django.core.exceptions import ValidationError
from forms import login_form
from repository.models import UserProfile
from django.core.exceptions import ValidationError


class RGFM(login_form.LGFM):
    # username = fields.CharField(
    #     max_length=20,
    #     min_length=5,
    #     error_messages={'required': "用户名不能为空", 'min_length': '用户名最少5个字符', 'max_length': '用户名最多20个字符'},
    #     widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': "请输入用户名"})
    # )
    # password = fields.CharField(
    #     max_length=12,
    #     min_length=6,
    #     error_messages={'required': '密码不能为空', 'min_length': "长度不能小于6", "max_length": "长度不能大于12"},
    #     widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': "请输入密码"})
    # )
    re_password = fields.CharField(
        max_length=12,
        min_length=6,
        error_messages={'required': '密码不能为空', 'min_length': "长度不能小于6", "max_length": "长度不能大于12"},
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': "请输入密码"})
    )
    email = fields.EmailField(
        error_messages={'required': '邮箱不能为空', 'invalid': "邮箱格式错误"},
        widget=widgets.EmailInput(attrs={'class': "form-control", 'placeholder': "请输入邮箱地址", 'autocomplete': "off"})
    )

    def __init__(self, *args, **kwargs):
        # dic = {'username': '', 'password': ''}
        super(RGFM, self).__init__(*args, **kwargs)
        # print("init registe form")
        self.name = ""
        self.pwd = ""
        self.email = ""
        # self.fields['username'] = kwargs.get('username')
        # self.fields['password'] = kwargs.get('password')

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # print("rgrg:", pwd)
        return pwd

    def clean(self):
        """
        重写clean主要用于本项目的两次密码输入一致性校验
        :return:
        """
        cleaned_data = self.cleaned_data
        # print("rgpwd:", cleaned_data)
        pwd = cleaned_data.get('password', None)
        pwd2 = cleaned_data.get('re_password', None)
        # print(pwd, pwd2)
        if pwd != pwd2:
            raise forms.ValidationError("两次输入密码不一致!")
        else:
            self.name = cleaned_data.get('username', None)
            self.pwd = cleaned_data.get('password', None)
            self.email = cleaned_data.get('email', None)
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserProfile.objects.filter(email=email).filter():
            raise ValidationError('邮箱已被使用!', 'invalid')  # 这里会返回到前端显示
        return email

    def get_registe_info(self):
        # print("get name")
        return self.name, self.pwd, self.email
