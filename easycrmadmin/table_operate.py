from django.utils import timezone
from django.db.models import Count, Q
import time


def table_filter(request, admin_class):
    """
    根据自定义过滤(筛选)字段查询数据
    :param request:
    :param admin_class:
    :return: 查询后的数据
    """
    filter_conditions = {}
    if hasattr(admin_class, 'list_filter'):  # 判断这张表是否自定义了可筛选字段
        for condition in admin_class.list_filter:
            if request.GET.get(condition):  # 前端有根据筛选字段进行数据请求
                field_type = admin_class.model._meta.get_field(condition).__repr__()  # <django.db.models.fields.CharField: source>
                # print("field type++:", field_type)
                if 'ForeignKey' in field_type:  # 外键类型
                    filter_conditions['%s_id' % condition] = request.GET.get(condition)
                elif 'DateField' in field_type:  # 日期类型
                    filter_conditions['%s__gt' % condition] = request.GET.get(condition)
                elif 'ManyToMany' in field_type:  # 多对多类型
                    pass
    print("filter conditions: ", filter_conditions)
    return admin_class.model.objects.filter(**filter_conditions)


def table_search(request, querysets, admin_class):
    """
    根据自定义搜索字段查询数据
    :param request:
    :param querysets: 过滤后的querysets
    :param admin_class:
    :return: 查询后的数据
    """
    search_condition = request.GET.get("q")
    if search_condition:
        q_objs = []
        for q_filed in admin_class.search_fields:
            q_objs.append("Q(%s__contains='%s')" % (q_filed, search_condition))
        return querysets.filter(eval("|".join(q_objs)))
    return querysets


def table_orderby(request, querysets, admin_class):
    """
    根据前端请求字段排序数据
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    print(table_orderby.__name__)
    ordered_colnumber = -1
    # print("will to order data:", querysets)
    # print("admin_class:", admin_class)
    orderby_field = request.GET.get('orderby')  # 排序的字段
    if orderby_field:
        # print("orderby_field:", orderby_field)
        # print(dir(querysets))
        ordered_obj = querysets.order_by(orderby_field)
        if orderby_field in admin_class.list_display:
            ordered_colnumber = admin_class.list_display.index(orderby_field.strip('-'))  # 字段在哪一列
            if orderby_field.startswith("-"):  # 做这个操作的目的是方便数据库操作!
                orderby_field = orderby_field.strip("-")
            else:
                orderby_field = "-%s" % orderby_field
            return [ordered_obj, orderby_field, ordered_colnumber]
    return [querysets, orderby_field, None]


class TableHandler(object):
    # 根据实际情况初始化一些数据
    def __init__(self, request, admin_class, queryset, order_res):
        self.request = request
        self.admin_class = admin_class
        self.model_class = admin_class.model
        self.model_verbose_name = self.model_class._meta.verbose_name
        self.model_name = self.model_class._meta.model_name

        self.readonly_table = admin_class.readonly_table  # 整张表是否只读
        self.readonly_fields = admin_class.readonly_fields  # 只读的字段
        self.list_display = admin_class.list_display  # 可显示的字段
        self.list_editable = admin_class.list_editable  # 可编辑的字段
        self.list_filter = self.get_list_filter(admin_class.list_filter)  # 可筛选的字段
        self.search_fields = admin_class.search_fields  # 可搜索的字段
        self.actions = admin_class.actions  # action

        self.ordered_field = order_res[1]  # 保存已经进行排序的字段返回给前端用
        self.ordered_field_colnumber = order_res[2]  # 保存已排序字段的列号给前端用
        self.query_sets = queryset

    def get_list_filter(self, list_filter):
        self.list_filter = []
        filters = []
        # print("list filters", list_filter)
        for i in list_filter:
            col_obj = self.model_class._meta.get_field(i)
            # print("col obj", col_obj)  # 具体某字段
            data = {
                'verbose_name': col_obj.verbose_name,
                'column_name': i,
            }
            print("字段类型:", col_obj.deconstruct()[1])  # 序列化对象获得类型
            if col_obj.deconstruct()[1] not in ('django.db.models.DateField', 'django.db.models.DateTimeField'):
                try:
                    print("ok:", col_obj.get_choices())
                    choices = col_obj.get_choices()

                except AttributeError as e:
                    choices_list = col_obj.model.objects.values(i).annotate(count=Count(i))
                    print(choices_list)
                    choices = [[obj[i], obj[i]] for obj in choices_list]
                    choices.insert(0, ['', '----------'])
            else:  # 特殊处理datefield
                today_obj = timezone.datetime.now()
                choices = [
                    ('', '---------'),
                    (today_obj.strftime("%Y-%m-%d"), '今天'),
                    ((today_obj - timezone.timedelta(days=7)).strftime("%Y-%m-%d"), '过去7天'),
                    ((today_obj - timezone.timedelta(days=today_obj.day)).strftime("%Y-%m-%d"), '本月'),
                    ((today_obj - timezone.timedelta(days=90)).strftime("%Y-%m-%d"), '过去3个月'),
                    ((today_obj - timezone.timedelta(days=180)).strftime("%Y-%m-%d"), '过去6个月'),
                    ((today_obj - timezone.timedelta(days=365)).strftime("%Y-%m-%d"), '过去1年'),
                    ((today_obj - timezone.timedelta(seconds=time.time())).strftime("%Y-%m-%d"), 'ALL'),
                ]
                # print(choices)
            data['choices'] = choices

            # handle selected data
            if self.request.GET.get(i):  # 这里主要是处理提交过滤后,原来下拉框还是显示上次选择的选项
                # print("selected:", self.request.GET.get(i))
                # print(type(self.request.GET.get(i)))
                data['selected'] = self.request.GET.get(i)
            filters.append(data)
        # print(filters)

        return filters
