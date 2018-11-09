# 自定义标签公共库,供前端回调
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def load_menus(request):
    """
    获取非管理员用户左边栏菜单项目
    :param request:
    :return:
    """
    menus = []
    print("request info", request)
    print(dir(request.user))
    print("登陆账户名:", request.user.name)
    print(request.user.roles)

    print(request.user.roles.select_related())  # 因为是多对多,所以一并查找出来
    for role in request.user.roles.select_related():
        menus.extend(role.menus.select_related())
    print("menus:", menus)
    return set(menus)


@register.simple_tag
def get_db_table_name(table_admin_class):
    """
    获取表名
    :param request:
    :param classToModel: 跟表绑定关系的AdminClass,根据AdminClass可以获取对用model class的信息
    :return:
    """
    # print(dir(table_admin_class))
    # print(table_admin_class.model._meta.model_name)
    # print(table_admin_class.model._meta.verbose_name)
    return table_admin_class.model._meta.verbose_name


def render_list_editable_column(table_obj, row_obj, field_obj):
    #print(table_obj,row_obj,field_obj,field_obj.name,field_obj.get_internal_type())
    # 判断现在这个字段是不是属于括号里的类型,不同类型需要分别处理
    if field_obj.get_internal_type() in ("CharField", "ForeignKey", "BigIntegerField", "IntegerField"):
        # print("this place:", field_obj)
        # print("row obj:", row_obj)
        # print(dir(field_obj))
        # print(field_obj.attname)
        # print(field_obj.cached_col)
        # print(field_obj._verbose_name)
        # print(field_obj.blank)
        # print(field_obj.column)
        # print(field_obj.get_attname_column(row_obj))
        # print(field_obj.get_col())
        # print(field_obj.choices)
        # print(field_obj._check_choices)  # 判断哪个字段是choice属性

        column_data = field_obj.value_from_object(row_obj)  # 通过行对象获取到对应列的值
        if not field_obj.choices and field_obj.get_internal_type() != "ForeignKey":
            column = '''<input data-tag='editable' type='text' name='%s' value='%s' >''' %\
                     (field_obj.name, field_obj.value_from_object(row_obj) or '')

        else:
            column = '''<select data-tag='editable' class='form-control'  name='%s' >''' % field_obj.name

            for option in field_obj.get_choices():
                if option[0] == column_data:
                    selected_attr = "selected"
                else:
                    selected_attr = ''
                column += '''<option value='%s' %s >%s</option>''' % (option[0], selected_attr, option[1])
            column += "</select>"
    elif field_obj.get_internal_type() == 'BooleanField':
        # column_data = field_obj._get_val_from_obj(row_obj)  # Django1.9版本不再支持这个写法,因为这个问题耽误好长时间,value_from_object
        column_data = field_obj.value_from_object(row_obj)
        if column_data:
            checked = 'checked'
        else:
            checked = ''
        column = '''<input data-tag='editable'   type='checkbox' name='%s' value="%s"  %s> ''' % (field_obj.name,
                                                                                                  column_data,
                                                                                                  checked)
    else:
        # column = field_obj._get_val_from_obj(row_obj)
        column = field_obj.value_from_object(row_obj)
    return column


@register.simple_tag
def build_table_row(row_obj, table_obj):
    """
    组表数据
    :param row_obj: 每一行数据的对象
    :param table_obj: 哪张表的对象
    :return: 生成html标签字符串形式给前端
    """
    row_ele = "<tr>"
    row_ele += "<td><input type='checkbox' tag='row-check' value='%s'></td>" % row_obj.id
    if table_obj.list_display:
        for index, column_name in enumerate(table_obj.list_display):
            column = ""
            # print(column_name)  # 列名,显示哪些信息
            if hasattr(row_obj, column_name):  # 有没有这一列
                field_obj = row_obj._meta.get_field(column_name)
                column_data = field_obj.value_from_object(row_obj)
                # print(dir(field_obj))
                if field_obj.choices:
                    # print(dir(row_obj))
                    # print("qqqqq:", row_obj._get_FIELD_display(field_obj))
                    # print("qqqqq:", field_obj)
                    column_data = row_obj._get_FIELD_display(field_obj)
                    # column_data = getattr(row_obj, "get_%s_display" % column_name)  # 这个用法也在最新的Django版本中作废了
                else:
                    column_data = getattr(row_obj, column_name)
                if 'DataTimeField' in field_obj.__repr__():
                    column_data = getattr(row_obj, column_name).strftime("%Y-%m-%d %H:%M:%S")
                if 'ManyToManyField' in field_obj.__repr__():
                    column_data = getattr(row_obj, column_name).select_related().count()
                # print("column data:", column_data)
                # print("00column :", column)
                if index == 0:  # 首列 可点击进入更改页  ,这里 逻辑感觉有些乱,后续再调整下吧
                    column = '''<td><a class='btn-link'  href='%smodify/%s/' >%s</a> </td> ''' % (
                        table_obj.request.path,
                        row_obj.id,
                        column_data)
                    # print("00column:", column)
                # print("edit:", table_obj.list_editable)
                else:
                    if column_name in table_obj.list_editable:  # 可编辑的列
                        column = "<td>%s</td>" % render_list_editable_column(table_obj, row_obj, field_obj)
                    else:
                        column = "<td>%s</td>" % column_data
            elif hasattr(table_obj.admin_class, column_name):
                field_func = getattr(table_obj.admin_class, column_name)
                table_obj.admin_class.instance = row_obj
                column = "<td>%s</td>" % field_func(table_obj.admin_class)
            row_ele += column
            # print("row ele:", row_ele)
    else:
        # print("else else else")
        row_ele += "<td><a class='btn-link' href='{request_path}change/{obj_id}/'>{column}</a></td>".format(
            request_path=table_obj.request.path, column=row_obj, obj_id=row_obj.id)

    row_ele += "</tr>"
    # print("xx:", row_ele)
    return mark_safe(row_ele)


@register.simple_tag
def get_table_column(column, table_obj):
    """
    获取表单中列名
    :param column: 列字段名
    :param table_obj: 表对象
    :return: 列注释名
    """
    print(table_obj)
    if hasattr(table_obj.model_class, column):
        return table_obj.model_class._meta.get_field(column).verbose_name
    else:  # 自定义非表中但要在前端显示在表单中的字段
        if hasattr(table_obj.admin_class, column):
            field_func = getattr(table_obj.admin_class, column)
            if hasattr(field_func, 'display_name'):
                return field_func.display_name
            return field_func.__name__


@register.simple_tag
def get_column_name(column):
    re_column = column
    if column.startswith("-"):
        re_column = column.strip("-")
    return re_column


@register.simple_tag
def display_obj_related(objs):
    """把对象及所有相关联的数据取出来"""
    pass


@register.simple_tag
def get_contract(enroll_obj):
    return enroll_obj.course_grade.contract.template.format(customer_name=enroll_obj.customer.name,
                                                            course_name=enroll_obj.course_grade.course.name)
