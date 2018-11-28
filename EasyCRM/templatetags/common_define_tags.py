# 自定义标签公共库,供前端回调
from django import template
from repository import models
from django.utils.safestring import mark_safe
from django.db.models import Sum
register = template.Library()


@register.simple_tag
def load_menus(request):
    """
    获取非管理员用户左边栏菜单项目
    :param request:
    :return:
    """
    menus = []
    # print("request info", request)
    # print(dir(request.user))
    # print("登陆账户名:", request.user.name)

    # print(request.user.roles.select_related())  # 因为是多对多,所以一并查找出来
    for role in request.user.roles.select_related():
        menus.extend(role.menus.select_related())
    # print("menus:", menus)
    return set(menus)


@register.simple_tag
def get_db_table_name(admin_class):
    """
    获取表名
    :param request:
    :param admin_class: 跟表绑定关系的AdminClass,根据AdminClass可以获取对用model class的信息
    :return:
    """
    # print(dir(table_admin_class))
    # print(table_admin_class.model._meta.model_name)
    # print(table_admin_class.model._meta.verbose_name)
    return admin_class.model._meta.verbose_name


def render_list_editable_column(table_obj, row_obj, field_obj):
    """

    :param table_obj:
    :param row_obj: 行
    :param field_obj: 列
    :return:
    """
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

        column_data = field_obj.value_from_object(row_obj)  # 通过行列定位到对应列的值
        if not field_obj.choices and field_obj.get_internal_type() != "ForeignKey":
            column = '''<input data-tag='editable' type='text' name='%s' value='%s' >''' %\
                     (field_obj.name, field_obj.value_from_object(row_obj) or '')

        else:
            column = '''<select data-tag='editable' class='form-control'  name='%s' >''' % field_obj.name

            for option in field_obj.get_choices():
                if option[0] == column_data:  # 下拉框对应条目选中
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
    :param row_obj: 每一条记录
    :param table_obj: 哪张表
    :return: 生成html标签字符串形式给前端
    """
    row_ele = "<tr>"
    row_ele += "<td><input type='checkbox' tag='row-check' value='%s'></td>" % row_obj.id
    if table_obj.list_display:
        for index, column_name in enumerate(table_obj.list_display):
            column = ""
            # print(column_name)  # 列名,显示哪些信息
            if hasattr(row_obj, column_name):  # 这一条数据有没有这个属性
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
    # print(table_obj)
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
    """
    初始报名表信息,目前必须先加号合同模板,没有对无合同模板的情况做异常处理
    :param enroll_obj:
    :return:
    """
    print("获取报名人信息:", enroll_obj)
    return enroll_obj.course_grade.contract.template.format(customer_name=enroll_obj.customer.name,
                                                            course_name=enroll_obj.course_grade.course.name)


@register.simple_tag
def load_search_element(table_obj):
    """
    创建搜索框
    :param table_obj:
    :return:
    """
    # print("load_search_element:", table_obj.request.GET)
    # print("table obj model class:", table_obj.model_class)
    # print(table_obj.search_fields)

    if table_obj.search_fields:
        already_exist_ars = ''
        for k, v in table_obj.request.GET.items():
            if k != 'q':
                already_exist_ars += "<input type='hidden' name='%s' value='%s' >" % (k, v)
        # print(table_obj.model_class._meta.get_field('qq').verbose_name)
        # print(table_obj.model_class._meta.get_field('phone').verbose_name)
        # print(map(lambda x: table_obj.model_class._meta.get_field(x).verbose_name, table_obj.search_fields))
        placeholder = "请根据 %s 搜索" % ",".join(map(lambda x: table_obj.model_class._meta.get_field(x).verbose_name, table_obj.search_fields))
        ele = """
            <div class="searchbox">
                   <form method="GET">
                    <div class="input-group custom-search-form">
                        <input type="text" name="q" value='%s' class="form-control col-lg-3" placeholder="%s">
                        %s
                        &nbsp
                        <span class="input-group-btn">
                            <button type="submit" class="btn btn-primary">搜索</button>
                        </span>
                    </div>
               </form>
           </div>
            """ % (table_obj.request.GET.get('q') if table_obj.request.GET.get('q') else '',
                   placeholder, already_exist_ars)
        return mark_safe(ele)
    return ''


@register.simple_tag
def load_admin_actions(table_obj):
    select_ele = "<select id='admin_action' name='admin_action' class='form-control'><option value=''>----</option>"
    for option in table_obj.actions:
        action_display_name = option  # 批量操作中文显示
        if hasattr(table_obj.admin_class, option):
            action_func = getattr(table_obj.admin_class, option)
            if hasattr(action_func, 'short_description'):  # 自定义一个中文注释
                action_display_name = action_func.short_description
        select_ele += ("<option value=%s>" % option) + action_display_name + "</option>"
    select_ele += "</select>"
    return mark_safe(select_ele)


@register.simple_tag
def get_course_record_url(class_obj):
    # print("get_course_record_url:", class_obj)
    # print(models.CourseRecord._meta.app_label)
    # print(models.CourseRecord._meta.model_name)
    # print(class_obj.id)
    return "%s/%s/%s/" % (models.CourseRecord._meta.app_label, models.CourseRecord._meta.model_name, class_obj.id)
    # return models.CourseRecord._meta.app_label, models.CourseRecord._meta.model_name, class_obj.id


@register.simple_tag
def get_course_grades(class_obj):
    """
    返回整个班的成绩
    :param class_obj:
    :return:
    """
    # print("get_course_grades")
    objs = None
    try:
        objs = models.StudyRecord.objects.filter(course_record__from_class=class_obj).values_list('student').annotate(Sum('score'))
        print("cs_obj:", objs)
    except Exception as e:
        pass
    return dict(objs)


@register.simple_tag
def get_course_ranking(class_grade_dic):
    """
    返回整个班的排名
    :param class_grade_dic:
    :return:
    """
    # print("排名前:", class_grade_dic)
    ranking_dict = {}
    # ranking_list = sorted(class_grade_dic.items(), key=lambda x: x[1], reverse=True)  # 降序
    ranking_list = sorted(class_grade_dic.items(), key=lambda x: x[1])  # 默认是升序
    reverse_rk_list = list(reversed(ranking_list))
    for item in reverse_rk_list:
        ranking_dict[item[0]] = [item[1], reverse_rk_list.index(item)+1]
    # print(ranking_dict)
    return ranking_dict


@register.simple_tag
def get_stu_grade_ranking(course_ranking_dic, enroll_obj):
    """
    返回这个学生在本班的成绩排名
    :param course_ranking_dic:
    :param enroll_obj:
    :return:
    """
    score = course_ranking_dic.get(enroll_obj.id)
    if score:
        return score[1]


@register.simple_tag
def fetch_stu_course_score(class_grade_dic, enroll_obj):
    print(class_grade_dic.get(enroll_obj.id))
    return class_grade_dic.get(enroll_obj.id)


@register.simple_tag
def get_study_record_count(enroll_obj):
    print("enroll_obj:", enroll_obj)
    study_records = []
    course_records = enroll_obj.course_grade.courserecord_set.select_related()  # 反查
    for obj in course_records:
        # print(obj)
        study_records.extend(obj.studyrecord_set.select_related().filter(student=enroll_obj))
    # print(study_records)
    # for i in study_records:
    #     print(i.score_choices)  # ((100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (70, 'B-'), (60, 'C+'), (50, 'C'), (40, 'C-'), (-50, 'D'), (0, 'N/A'), (-100, 'COPY'), (-1000, 'FAIL'))
    return study_records


@register.simple_tag
def get_study_record(course_record, enroll_obj):
    study_record_obj = course_record.studyrecord_set.select_related().filter(student=enroll_obj)
    print("study_record_obj:", study_record_obj)
    if study_record_obj:
        return study_record_obj[0]


@register.simple_tag
def get_course_score(study_records):
    # 目前课程的学分
    score = 0
    for index in study_records:
        score += index.score
    return score
