from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib.auth.decorators import login_required
from easycrmadmin import views as easyadmin_views
from forms import ad_forms
from repository import models
from market.easy_admin import site
from forms import stu_form
from django.core.cache import cache
from django.contrib.auth.models import Permission
import json
import os
from EasyCRM.settings import ENROLLED_DATA
from easycrmadmin import permission_control
# Create your views here.

had_allote_permission = False


def allote_market_permissions(request):
    if Permission.objects.get(codename='this_table'):
        perm_obj = Permission.objects.get(codename='this_table')
        request.user.user_permissions.add(perm_obj)
    if Permission.objects.get(codename='table_modify'):
        perm_obj = Permission.objects.get(codename='table_modify')
        request.user.user_permissions.add(perm_obj)
    if Permission.objects.get(codename='table_add'):
        perm_obj = Permission.objects.get(codename='table_add')
        request.user.user_permissions.add(perm_obj)
    if Permission.objects.get(codename='table_delete'):
        perm_obj = Permission.objects.get(codename='table_add')
        request.user.user_permissions.add(perm_obj)

    global had_allote_permission
    had_allote_permission = True


@login_required
@permission_control.check_permission
def main_pg(request):
    # print('market')
    if had_allote_permission is False:
        print("为销售分配权限")
        allote_market_permissions(request)
    return render(request, 'market/market_main_pg.html')


@login_required
def customers(request):
    """
    浏览客户信息,这里直接调用easycrmadmin中的客户库显示函数
    :param request:
    :return:
    """
    # 分配权限

    tp_data = easyadmin_views.table_display(request, 'repository', 'customer', innercall=True)
    # print("tp:", tp_data)
    return render(request, 'market/market_customers.html', tp_data)


@login_required
def customers_modify(request, nid):
    """
    修改客户信息
    :param request:
    :param nid: 要修改的客户ID
    :return:
    """
    # print("customer_modify")
    template_data = easyadmin_views.table_modify(request, 'repository', 'customer', nid, innercall=True)
    if type(template_data) is dict:
        return render(request, 'market/market_customers_change.html', template_data)
    else:
        return template_data


@login_required
def my_customers(request):
    """
    浏览自己的客户库
    :param request:
    :return:
    """
    # print("my_customers")
    admin_table_list_url = reverse('this_table', args=('repository', 'customer',))
    # u_obj = models.UserProfile.objects.filter(name=request.user.name)
    # print(request.user.id)

    return redirect(admin_table_list_url+'?consultant=%s' % request.user.id)


@login_required
def enrollment(request, nid):
    """
    帮助客户完成注册成为学员
    :param request:
    :param nid: 要注册的客户ID
    :return:
    """
    print("enrollment user id :", nid)
    fields = []
    result_msg = {'pass': 0, 'step': 1}  # 初始在第一步
    try:
        customer_obj = models.Customer.objects.get(id=nid)
        for field_obj in models.Enrollment._meta.fields:
            if field_obj.editable:
                fields.append(field_obj.name)
                # print(field_obj.name)
        # print("useful func:", site.enabled_funcs)
        model_form = ad_forms.init_modelform(models.Enrollment, fields,
                                             site.enabled_funcs[models.Enrollment._meta.app_label][models.Enrollment._meta.model_name])
        form = model_form()
        if request.method == "POST":
            if request.POST.get('paid_fee'):
                enroll_obj = None
                print(request.POST)
                fields = []
                for field_obj in models.PaymentRecord._meta.fields:
                    if field_obj.editable:
                        fields.append(field_obj.name)
                model_form = ad_forms.init_modelform(models.PaymentRecord, fields,
                                                     site.enabled_funcs[models.PaymentRecord._meta.app_label][models.PaymentRecord._meta.model_name])

                form = model_form(request.POST)
                if form.is_valid():
                    print("报名成功")
                    form.save()
                    enroll_obj = form.instance.enrollment
                    customer_obj.status = "signed"  # 更新客户表报名状态
                    customer_obj.save()
                    result_msg = {'pass': 4, 'step': 5, 'msg': "报名成功"}
                return render(request, 'market/market_enrollment.html', {"response": result_msg,
                                                                         'enroll_obj': enroll_obj})

            post_data = request.POST.copy()
            print("POST DATA:", post_data)
            form = model_form(post_data)
            print(form.is_valid())
            # print(form.errors)
            # print("form:", form)
            # print("grade:", request.POST.get('course_grade'))
            # # 判断是不是已经有报名记录了
            if form.is_valid():
                existed_enrollment_obj = models.Enrollment.objects.filter(customer=customer_obj,
                                                                          course_grade_id=request.POST.get('course_grade'))
                print("existed_enrollment_obj:", existed_enrollment_obj)
                if existed_enrollment_obj:
                    if existed_enrollment_obj.filter(contract_agreed=True):
                        # 学员是否已经确认填好报名表了
                        enroll_obj = existed_enrollment_obj.get(contract_agreed=True)
                        if enroll_obj.contract_approved or request.POST.get('contract_approved') == "on":
                            print("enrollment passed")
                            # 审核通过了
                            enroll_obj.contract_approved = True
                            enroll_obj.save()

                            if enroll_obj.paymentrecord_set.select_related().count() > 0:  # 查学员是否已经缴费
                                result_msg = {'pass': 1, 'step': 5}
                                print("enrollment success")
                            else:
                                # 等待假设财务核实账目
                                fields = []
                                for field_obj in models.PaymentRecord._meta.fields:
                                    if field_obj.editable:
                                        fields.append(field_obj.name)
                                print("fields:", fields)
                                print("what the:", site.enabled_funcs[models.PaymentRecord._meta.app_label][models.PaymentRecord._meta.model_name])
                                model_form = ad_forms.init_modelform(models.PaymentRecord,
                                                                     fields,
                                                                     site.enabled_funcs[models.PaymentRecord._meta.app_label][models.PaymentRecord._meta.model_name])
                                form = model_form()
                                result_msg = {'pass': 3, 'step': 4, 'msg': "等待财务核实"}
                                return render(request, 'market/market_enrollment.html', {"payment_form": form,
                                                                                         "customer_obj": customer_obj,
                                                                                         'enroll_obj': enroll_obj,
                                                                                         "response": result_msg})

                        else:
                            result_msg = {'pass': 2, 'step': 3, 'msg': "等待审核", 'enroll_obj': form.instance}
                        form = model_form(post_data, instance=enroll_obj)
                    else:
                        print("id:", form.instance.id)
                        result_msg = {'pass': 1, 'step': 2, 'msg': "等待学生签合同", 'enroll_obj': existed_enrollment_obj[0]}

                else:
                    form.save()
                    cache.set(form.instance.id, "available time", 30*60)  # 报名链接半小时的有效时间,报名链接动态字符串后续完善把
                    print("id:", form.instance.id)
                    result_msg = {'pass': 1, 'step': 2, 'enroll_obj': form.instance}
                    print("enrollment save")
            else:
                # response = form.errors
                # print("errors:", response)

                # info = ""
                # for index in form.errors:
                #     # print(index)
                #     if index != '__all__':
                        # print(models.Enrollment._meta.get_field(index).verbose_name)
                        # print(form.errors[index])
                        # info += (models.Enrollment._meta.get_field(index).verbose_name + ":" + form.errors[index] + '\n')
                # print(info)
                result_msg = {'pass': 0, 'step': 1, 'msg': "填表有误!"}
                # result_msg.update({'msg': info})
        print(result_msg)
        return render(request, 'market/market_enrollment.html', {"enrollment_form": form,
                                                                 "customer_obj": customer_obj,
                                                                 "response": result_msg})
    except models.Customer.DoesNotExist as ex:
        return HttpResponse("客户不存在了")


def stu_enrollment(request, enrollment_id):
    """
    交给学生填写的报名页
    :param request:
    :param enrollment_id:报名表ID
    :return:
    """
    print("stu_enrollment:", enrollment_id)
    if cache.get(enrollment_id) == "available time":

        try:
            enroll_obj = models.Enrollment.objects.get(id=enrollment_id)
            if request.method == "GET":
                contract_form = stu_form.CustomerForm(instance=enroll_obj.customer)
            elif request.method == "POST":
                # print("选择情况:", request.POST.get("contract_agreed"))
                # if request.POST.get("contract_agreed") == "on":
                #     pass
                if request.is_ajax():  # 处理图片
                    print(request.FILES)
                    save_path = "%s%s%s" % (ENROLLED_DATA, os.sep, enrollment_id)
                    if not os.path.exists(save_path):
                        os.makedirs(save_path, exist_ok=True)
                    print("save path:", save_path)
                    for k, v in request.FILES.items():
                        print("file name:", v.name)
                        with open("%s%s%s" % (save_path, os.sep, v.name), 'wb') as fw:  # 针对不同机器可能会有写入权限的问题.
                            for chunk in v.chunks():
                                fw.write(chunk)
                    return HttpResponse("上传成功")
                print(request.POST)
                contract_form = stu_form.CustomerForm(request.POST, instance=enroll_obj.customer)
                # print("更新后:", customer_form)
                if contract_form.is_valid():
                    print("没有问题")
                    contract_form.save()
                    if request.POST.get("contract_agreed") == "on":
                        enroll_obj.contract_agreed = True
                    enroll_obj.save()
                    print("签字情况:", enroll_obj.contract_agreed)
                    return HttpResponse("报名成功了!")
                else:
                    print(contract_form.errors)
            return render(request, 'market/stu_enrollment.html', {'enroll_obj': enroll_obj, 'customer_form': contract_form})
        except models.Enrollment.DoesNotExist as es:
            return HttpResponse("报名表不见了.")
    else:
        print("链接失效了")
        return HttpResponse("链接失效了,请重新联系客服申请")
