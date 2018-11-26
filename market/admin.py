# 自定义admin显示, 如何配置请查看官方文档:https://docs.djangoproject.com/en/2.1/topics/auth/customizing/
from django.contrib import admin
from django import forms

from repository import models

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# Register your models here.
print("market")  # 这里会在Django启动的时候执行


class UserCreationForm(forms.ModelForm):
    """
    Django admin配置界面添加用户时的界面表单认证
    """
    password1 = forms.CharField(label='输入密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and (password1 != password2):
            raise forms.ValidationError("输入密码不一致!")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Django admin配置界面 修改用户时的界面表单认证
    """
    # 会显示在前端页面上
    password = ReadOnlyPasswordHashField(label="密码",
                                         help_text="重新设置密码请""点击这里--><a href=\"../password/\">修改密码</a>.")

    class Meta:
        model = models.UserProfile
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'email', 'is_admin', 'is_active')
    list_filter = ('is_admin', )
    # list_editable = ['is_admin']
    # 设置fieldsets 控制管理“添加”和 “更改” 页面的布局{分类标题: {'fields'}: ('字段名1', '字段名2')}
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('name',)}),
        ('权限', {'fields': ('is_admin',)}),
        # ('权限', {'fields': ('is_admin', 'user_permissions', 'roles')}),
    )
    # 不加下面这个属性会出错,原因看笔记和https://github.com/django/django/blob/master/django/contrib/auth/admin.py#L47
    # dd_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', )
    ordering = ('email', )
    # filter_horizontal = ('user_permissions', 'groups', 'roles')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('qq', 'name', 'source', 'phone', 'course', 'class_type', 'consultant', 'status', 'date')
    choice_fields = ('status', 'source', 'class_type')
    fk_fields = ('consultant', 'course')
    list_per_page = 10
    list_filter = ('name', 'source', 'course', 'status', 'date', 'class_type', 'consultant')
    list_editable = ['phone', ]


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_type', 'url_name', 'order')
    filter_horizontal = ('sub_menus',)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('menus',)


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'course_grade', 'school', 'enrolled_date', 'contract_agreed', 'contract_approved')


class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'pay_type', 'paid_fee', 'date', 'consultant')


class StudyRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course_record', 'score', 'date', 'note')
    list_editable = ('student', 'score', 'course_record', 'note')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'period')


admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Branch)
admin.site.register(models.ClassList)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Enrollment, EnrollmentAdmin)
admin.site.register(models.StuAccount)
admin.site.register(models.CourseRecord)
admin.site.register(models.StudyRecord, StudyRecordAdmin)
admin.site.register(models.PaymentRecord, PaymentRecordAdmin)
