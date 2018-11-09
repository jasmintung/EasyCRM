from django.utils import timezone
from django.db.models import Count, Q
import time


def table_filter(request, admin_class, model_class):
    """
    前端有过滤数据
    :param request:
    :param admin_class:
    :param model_class:
    :return:
    """
    filter_conditions = {}
    if hasattr(admin_class, 'list_filter'):
        for condition in admin_class.list_filter:
            if request.GET.get(condition):
                field_type = model_class._meta.get_field(condition).__repr__()  # <django.db.models.fields.CharField: source>
                # print("field type++:", field_type)
                if 'ForeignKey' in field_type:  # 外键类型
                    filter_conditions['%s_id' % condition] = request.GET.get(condition)
                elif 'DateField' in field_type:  # 日期类型
                    filter_conditions['%s__gt' % condition] = request.GET.get(condition)
    print("filter conditions: ", filter_conditions)
    return model_class.objects.filter(**filter_conditions)


def table_search(request, querysets, admin_class):
    """前端有搜索数据"""
    return querysets


def table_orderby(request, querysets, admin_class):
    """
    根据字段名排序数据
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    print(table_orderby.__name__)
    ordered_colnumber = -1
    # print("will to order data:", querysets)
    # print("admin_class:", admin_class)
    orderby_field = request.GET.get('orderby')  # 排序的字段名
    if orderby_field:
        # print("orderby_field:", orderby_field)
        print(dir(querysets))
        ordered_obj = querysets.order_by(orderby_field)

        ordered_colnumber = admin_class.list_display.index(orderby_field.strip('-'))
        if orderby_field.startswith("-"):  # 做这个操作的目的是方便数据库操作!
            orderby_field = orderby_field.strip("-")
        else:
            orderby_field = "-%s" % orderby_field
        return [ordered_obj, orderby_field, ordered_colnumber]
    return [querysets, orderby_field, None]


class TableHandler(object):
    def __init__(self, request, model_class, admin_class, queryset, order_res):
        self.request = request
        self.admin_class = admin_class
        self.model_class = model_class
        self.model_verbose_name = self.model_class._meta.verbose_name
        self.model_name = self.model_class._meta.model_name
        self.actions = admin_class.actions
        self.list_editable = admin_class.list_editable
        self.query_sets = queryset
        self.ordered_field = order_res[1]  # 保存已经进行排序的字段返回给前端用
        self.ordered_field_colnumber = order_res[2]  # 保存已排序字段的列号给前端用
        print("zzzzzzzzzzzzzzz:", self.ordered_field)
        self.readonly_table = admin_class.readonly_table  # 整张表只读
        self.readonly_fields = admin_class.readonly_fields
        self.list_display = admin_class.list_display
        self.search_fields = admin_class.search_fields
        self.list_filter = self.get_list_filter(admin_class.list_filter)

    def get_list_filter(self, list_filter):
        self.list_filter = []
        filters = []
        # print("list filters", list_filter)
        for i in list_filter:
            col_obj = self.model_class._meta.get_field(i)
            # print("col obj", col_obj)  # 表具体某字段
            data = {
                'verbose_name': col_obj.verbose_name,
                'column_name': i,
            }
            # print("字段类型:", col_obj.deconstruct()[1])
            if col_obj.deconstruct()[1] not in ('django.db.models.DateField', 'django.db.models.DateTimeField'):
                try:
                    choices = col_obj.get_choices()

                except AttributeError as e:
                    choices_list = col_obj.model.objects.values(i).annotate(count=Count(i))
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
