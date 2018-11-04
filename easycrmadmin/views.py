from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
# Create your views here.
from EasyCRM import app_config
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from easycrmadmin.easycrm_admin import site
from easycrmadmin import table_operate
from forms import ad_forms
import json


def main_pg(request):
    print('easyadmin boot page')
    # return HttpResponse('easyadmin')
    print(site.enabled_funcs)
    return render(request, 'admin/easy_admin.html', {'enabled_apps': site.enabled_funcs})


def app_tables(request, app_name):
    enabled_tb_cls = {app_name: site.enabled_funcs[app_name]}
    print("t app_name:", app_name)
    return render(request, 'admin/easy_admin.html', {'enabled_apps': enabled_tb_cls, 'current_app': app_name})


def update_tb_rows(request, edit_datas, admin_class):
    """
    更新修改的数据
    :return:
    """
    for index in edit_datas:
        obj_id = index.get('id', None)
        try:
            if obj_id:
                obj = admin_class.model.objects.get(id=obj_id)
                model_form = ad_forms.init_modelform(admin_class.model, list(index.keys()),
                                                     admin_class, request=request, update_tb=True)
                form_obj = model_form(instance=obj, data=index)
                if form_obj.is_valid():
                    print("edit success.")
                    form_obj.save()
                else:
                    pass
        except Exception as ex:
            print(ex)
    return True, []


def table_display(request, app_name, table_name):
    """
    获取具体哪张表的数据
    :param request:
    :param app_name:
    :param table_name:
    :return:
    """
    # 判断是不是注册过的APP

    print("table_display")
    print("app name:", app_name)
    print("table name:", table_name)
    print(site.enabled_funcs)
    errors = []
    if app_name in site.enabled_funcs:
        # print("app in here!")
        if table_name in site.enabled_funcs[app_name]:
            # print("table in here!")
            admin_class = site.enabled_funcs[app_name][table_name]
            if request.method == "POST":
                # print("POST INFO:", request.POST)
                edited_datas = request.POST.get("editable_data")
                print(edited_datas)  # [{"source":"others","status":"signed","id":"1"},]
                if edited_datas:
                    edited_datas = json.loads(edited_datas)
                    update_tb_rows(request, edited_datas, admin_class)
                    # print(edited_datas)
                    for index in edited_datas:
                        print(index)  # {'source': 'others', 'status': 'signed', 'id': '1'}
                    # 更新对应数据

            print(admin_class)  # 获取到对应model class的AdminClass, <class 'easycrmadmin.easy_admin.CustomerAdmin'>
            print(admin_class.model)  # 获取到model class<class 'easycrmadmin.models.Customer'>
            filter_queryset = table_operate.table_filter(request, admin_class, admin_class.model)
            print("filter result:", filter_queryset)  # <QuerySet [<Customer: QQ:111231 -- Name:大野>, <Customer: QQ:412412412 -- Name:zhangtong>, <Customer: QQ:45613213165 -- Name:alex3714>]>
            search_queryset = table_operate.table_search(request, filter_queryset, admin_class)
            order_res = table_operate.table_orderby(request, search_queryset, admin_class)
            print("order result:", order_res)
            # 分页处理,使用Django自带的分页类
            paginator = Paginator(order_res[0], admin_class.list_per_page)
            page = request.GET.get('page')
            try:
                table_obj_list = paginator.get_page(page)  # 具体某一页的对象
            except PageNotAnInteger:
                table_obj_list = paginator.get_page(1)  # 返回到第一页的对象
            except EmptyPage:
                table_obj_list = paginator.get_page(paginator.num_pages)

            table_obj = table_operate.TableHandler(request, admin_class.model, admin_class, table_obj_list, order_res)
            return_data = {'table_obj': table_obj,
                           'app_name': app_name,
                           'paginator': paginator,
                           'errors': errors,
                           'enabled_func': site.enabled_funcs}
            return render(request, 'admin/model_obj_list.html', return_data)

    else:
        return HttpResponse("go ahead")


def table_modify(request, app_name, table_name, obj_nid):
    print(app_name, table_name, obj_nid)


def table_add(request, app_name, model_name):
    """
    表格添加
    :param request:
    :param app_name:
    :param model_name:
    :return:
    """
    # print(app_name, model_name)  # easycrmadmin customer
    # print(site.enabled_funcs)
    if app_name in site.enabled_funcs:
        if model_name in site.enabled_funcs[app_name]:
            fields = []
            admin_class = site.enabled_funcs[app_name][model_name]
            for field_obj in admin_class.model._meta.fields:
                # print("field_obj:", field_obj)
                # print("filed name:", field_obj.name)  # 表字段名
                if field_obj.editable:
                    fields.append(field_obj.name)
            for field_obj in admin_class.model._meta.many_to_many:
                fields.append(field_obj.name)
            model_form = ad_forms.init_modelform(admin_class.model, fields, admin_class)

            if request.method == "GET":
                form_obj = model_form()
            elif request.method == "POST":
                print("POST................................")
                print(request.POST)
                form_obj = model_form(request.POST)
                if form_obj.is_valid():
                    print("添加成功")
                    form_obj.save()
                else:
                    print("添加失败")
                    print(form_obj.errors)
                return redirect(request.path.rstrip('/add/'))
            print("form_obj:", form_obj)
            return render(request, 'admin/admin_tb_add.html',
                          {'form_obj': form_obj,
                           'model_name': admin_class.model._meta.model_name,
                           'admin_class': admin_class,
                           'app_name': app_name,
                           'enabled_admins': site.enabled_funcs})
