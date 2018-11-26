import re
from django import forms
from django.forms import fields
from django.forms import widgets
from repository.models import UserProfile
from django.core.exceptions import ValidationError


class LGFM(forms.Form):
    name = fields.CharField(
        max_length=20,
        min_length=5,
        error_messages={'required': "用户名不能为空", 'min_length': '用户名最少5个字符', 'max_length': '用户名最多20个字符'},
        widget=widgets.TextInput(attrs={'class': "form-control", 'placeholder': "请输入用户名"})
    )
    password = fields.CharField(
        max_length=12,
        min_length=6,
        error_messages={'required': '密码不能为空', 'min_length': "长度不能小于6", "max_length": "长度不能大于12"},
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': "请输入密码"})
    )

    def __init__(self, *args, **kwargs):
        super(LGFM, self).__init__(*args, **kwargs)
        print("init login form")
        # self.fields['username'] = kwargs.get('username')
        # self.fields['password'] = kwargs.get('password')

    def clean_password(self):
        """
        Form中字段中定义的匹配完成后,执行此方法进一步验证
        :return:
        """
        print("clean_username: go here!!")
        name = self.cleaned_data['username']
        pwd = self.cleaned_data['password']
        print(name)
        print(UserProfile.objects.filter(email=name))
        if UserProfile.objects.filter(username=name).first():
            if UserProfile.objects.filter(password=pwd).first():
                pass
            else:
                raise ValidationError('用户名或密码错误', 'invalid')  # 这里会返回到前端显示
        else:
            raise ValidationError('用户名或密码错误', 'invalid')  # 这里会返回到前端显示
        return pwd

    # def get_test(self):
    #     return self.cleaned_data.get('password')
