# 这里基本按照Django开发文档例子进行编写,客服操作自定制
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from easycrmadmin.easycrm_admin import BaseEasyCrmAdmin, site


from repository import models


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# class UserChangeForm(forms.ModelForm):
#     """A form for updating users. Includes all the fields on
#     the user, but replaces the password field with admin's
#     password hash display field.
#     """
#     password = ReadOnlyPasswordHashField()
#
#     class Meta:
#         model = MyUser
#         fields = ('email', 'password', 'date_of_birth', 'is_active', 'is_admin')
#
#     def clean_password(self):
#         # Regardless of what the user provides, return the initial value.
#         # This is done here, rather than on the field, because the
#         # field does not have access to the initial value
#         return self.initial["password"]


class UserProfileAdmin(BaseEasyCrmAdmin):
    # The forms to add and change user instances
    # form = UserChangeForm
    add_form = UserCreationForm
    model = models.UserProfile
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'email', 'is_staff', 'is_admin')
    list_filter = ('is_admin',)
    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     ('Personal info', {'fields': ('date_of_birth',)}),
    #     ('Permissions', {'fields': ('is_admin',)}),
    # )
    # # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # # overrides get_fieldsets to use this attribute when creating a user.
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'date_of_birth', 'password1', 'password2')}
    #     ),
    # )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class EnrollmentAdmin(BaseEasyCrmAdmin):
    model = models.Enrollment
    list_display = ['customer', 'school', 'course_grade', 'contract_agreed', 'contract_approved', 'enrolled_date']
    fk_fields = ['school', 'course_grade']
# Now register the new UserAdmin...


class CustomerAdmin(BaseEasyCrmAdmin):
    model = models.Customer
    # enroll字段用于表示不是表中的字段但前端显示时可以显示在同一张表信息中
    list_display = ['qq', 'qq_name', 'name', 'phone', 'source', 'consultant', 'status', 'date', 'enroll']
    list_editable = ['phone', 'source', 'consultant', 'status']
    list_filter = ['source', 'consultant', 'status']
    search_fields = ['qq', 'consultant__email']

    def enroll(self):
        """
        报名字段,用于客服帮助客户完成报名
        :return:
        """
        print("CustomerAdmin func:enroll", self)
        link_name = "开始报名"
        if self.instance.status == 'signed':
            link_name = "继续报名"
        return "<a class='btn-link' href='/market/enrollment/%s/'>%s</a>" % (self.instance.id, link_name)
    enroll.display_name = "报名链接"


print("market register")
site.register(models.UserProfile, UserProfileAdmin)
site.register(models.Customer, CustomerAdmin)
site.register(models.Enrollment, EnrollmentAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# site.unregister(Group)
