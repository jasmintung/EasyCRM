# Admin存在的意义是: 对前端控制可显示字段,可过滤(筛选)字段,可搜索字段,分页,多对多复选框,可编辑字段,只读字段,整表只读,action控制等
from django.shortcuts import redirect


class BaseEasyCrmAdmin(object):
    """自定义Admin基类"""
    list_display = []  # Set list_display to control which fields are displayed on the change list page of the admin
    list_filter = []  #
    fieldsets = ()  # Set fieldsets to control the layout of admin “add” and “change” pages.
    search_fields = []  # Set search_fields to enable a search box on the admin change list page
    ordering = None
    list_per_page = 10  # 每页显示多少条数据
    filter_horizontal = []  # 处理多对多关系复选框,https://docs.djangoproject.com/en/2.1/ref/contrib/admin/
    list_editable = []  # 同时必须在list_display中, allowing users to edit and save multiple rows at once
    readonly_fields = []  # fields不可修改
    actions = ['delete_selected_objs']  # 可以为所欲为的地方.比如批量删除,创建等
    readonly_table = False
    modelform_exclude_fields = []
    add_form = None

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        errors = {}
        if self.readonly_table:
            errors = {"readonly_tables": "这个表时是只读,不能被修改和删除!"}
        if not self.readonly_table:
            try:
                querysets.delete()  # 批量删除了
            except Exception as ex:
                print(ex)
        return redirect("/easycrmadmin/%s/%s" % (app_name, model_name))
    delete_selected_objs.short_description = "批量删除选择项目"


class EasySite(object):
    def __init__(self):
        self.enabled_funcs = {}  # 格式: {APP名称: {表名: 定制Admin_Class}}

    def register(self, model_class, admin_class=None):
        """
        自定义register
        :param model_class: model class名称
        :param admin_class: 定制Admin Class名称
        :return:
        """
        if model_class._meta.app_label not in self.enabled_funcs:
            print("app name:", model_class._meta.app_label)
            self.enabled_funcs[model_class._meta.app_label] = {}
        if not admin_class:  # 无定制admin
            admin_class = BaseEasyCrmAdmin()
        admin_class.model = model_class  # 绑定model class 和 admin
        self.enabled_funcs[model_class._meta.app_label][model_class._meta.model_name] = admin_class


site = EasySite()  # 其它APP都需要调用这个site中的register方法,来关联需要定制绑定的model class 和 Admin Class
