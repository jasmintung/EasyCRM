# 本来最开始是把model放在这里定义,但做的过程中发现就不太好用APP/ModelClass这样的访问关系
# 所以每个APP单独定义表结构,默认所有表结构全部放在管理员APP下,其它APP根据使用情况,单独定义然后增加关联关系
from django.contrib.auth.models import User
# Create your models here.
# ugettext_lazy() 将字符串作为惰性参照存储，而不是实际翻译。 翻译工作将在字符串在字符串上下文中被用到时进行，比如在Django管理页面提交模板时
from django.db import models
from easycrmadmin import models as ad_models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from repository import auth
# Create your models here.


class Customer(models.Model):
    """存储所有客户信息"""
    # 字段名称前加 u 表示后面字符串以 Unicode 格式 进行编码,一般用在中文字符串前面,防止因为源码储存格式问题,导致再次使用时出现乱码
    qq = models.CharField(max_length=64, unique=True, help_text=u'QQ号必须唯一')
    qq_name = models.CharField(u'QQ名称', max_length=64, blank=True, null=True)
    name = models.CharField(u'姓名', max_length=32, blank=True, null=True)
    sex_type = (('male', u'男'), ('female', u'女'))
    sex = models.CharField("u性别", choices=sex_type, default='male', max_length=32)
    birthday = models.DateField(u'出生日期', max_length=64, blank=True, null=True, help_text="格式yyyy-mm-dd")
    phone = models.BigIntegerField(u'手机号', blank=True, null=True)
    email = models.EmailField(u'常用邮箱', blank=True, null=True)
    id_num = models.CharField(u'身份证号', blank=True, null=True, max_length=64)
    source_type = (('qq', u"qq群"),
                   ('referral', u"内部转介绍"),
                   ('website', u"官方网站"),
                   ('baidu_ads', u"百度广告"),
                   ('qq_class', u"网易课堂"),
                   ('school_propaganda', u"高校宣讲"),
                   ('51cto', u"51CTO"),
                   ('others', u"其它"),
                   )
    # 这个客户来源渠道是为了以后统计用
    source = models.CharField(u'客户来源', max_length=64, choices=source_type, default='qq')
    # 假如新客户是老学员转介绍来了,如果是转介绍的,就在这里纪录是谁介绍的他,前提这个介绍人必须是我们的老学员,要不然系统里找不到
    referral_from = models.ForeignKey('self', verbose_name=u"转介绍自学员",
                                      help_text=u"若此客户是转介绍自内部学员,请在此处选择内部＼学员姓名",
                                      blank=True, null=True, related_name="internal_referral", on_delete=models.CASCADE)
    # 已开设的课程单独搞了张表，客户想咨询哪个课程，直接在这里关联就可以
    course = models.ForeignKey("Course", verbose_name=u"咨询课程", on_delete=models.CASCADE)
    class_type_choices = (('online', u'网络班'),
                          ('offline_weekend', u'面授班(周末)',),
                          ('offline_fulltime', u'面授班(脱产)',),
                          )
    class_type = models.CharField(u"班级类型", max_length=64, choices=class_type_choices)
    customer_note = models.TextField(u"客户咨询内容详情", help_text=u"客户咨询的大概情况,客户个人信息备注等...")
    work_status_choices = (('employed', '在职'), ('unemployed', '无业'))
    work_status = models.CharField(u"职业状态", choices=work_status_choices, max_length=32, default='employed')
    company = models.CharField(u"目前就职公司", max_length=64, blank=True, null=True)
    salary = models.CharField(u"当前薪资", max_length=64, blank=True, null=True)
    status_choices = (('signed', u"已报名"), ('unregistered', u"未报名"))
    status = models.CharField(u"状态", choices=status_choices, max_length=64,
                              default=u"unregistered", help_text=u"选择客户此时的状态")
    # 课程顾问,每个招生老师(销售)录入自己的客户
    consultant = models.ForeignKey("UserProfile", verbose_name=u"课程顾问", on_delete=models.CASCADE)
    date = models.DateField(u"咨询日期", auto_now_add=True)

    def __str__(self):
        return u"QQ:%s -- Name:%s" % (self.qq, self.name)  # 直接打印对象即可显示这个信息

    class Meta:  # 这个是用来在admin页面上展示的,因为默认显示的是表名,加上这个就变成中文啦
        verbose_name = u'客户信息表'
        verbose_name_plural = u"客户信息表"

    def clean_status(self):
        status = self.cleaned_data['status']
        if self.instance.id is None:  # add form
            if status == "signed":
                raise forms.ValidationError(("必须走完报名流程后，此字段才能改名已报名"))
            else:
                return status
        else:
            return status

    def clean_consultant(self):
        consultant = self.cleaned_data['consultant']

        if self.instance.id is None:  # add form这里写死课程顾问为当前登陆的销售
            return self._request.user

        elif consultant.id != self.instance.consultant.id:
            raise forms.ValidationError(('Invalid value: %(value)s 课程顾问不允许被修改,shoud be %(old_value)s'),
                                         code='invalid',
                                         params={'value': consultant, 'old_value': self.instance.consultant})
        else:
            return consultant


class Enrollment(models.Model):
    """存储学员报名的信息"""

    # 所有报名的学生 肯定是来源于客户信息表的,先咨询,后报名嘛
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    school = models.ForeignKey('Branch', verbose_name=u'校区', on_delete=models.CASCADE)

    # 选择报的班级, 班级是关联课程的
    course_grade = models.ForeignKey("ClassList", verbose_name=u"所报班级", on_delete=models.CASCADE)
    why_us = models.TextField(u"为什么选择我们?", max_length=1024, default=None, blank=True, null=True)
    your_expectation = models.TextField(u"学完想达到的具体期望", max_length=1024, blank=True, null=True)
    contract_agreed = models.BooleanField(u"我已认真阅读完培训协议并同意全部协议内容", default=False)
    contract_approved = models.BooleanField(u"审批通过", help_text=u"在审阅完学员的资料无误后勾选此项,合同即生效", default=False)
    enrolled_date = models.DateTimeField(auto_now_add=True, auto_created=True,
                                         verbose_name=u"报名日期")
    memo = models.TextField(u'备注', blank=True, null=True)

    def __str__(self):
        return "<%s  课程:%s>" % (self.customer, self.course_grade)

    class Meta:
        verbose_name = '学员报名表'
        verbose_name_plural = "学员报名表"
        unique_together = ("customer", "course_grade")
        # 这里为什么要做个unique_together联合唯一?因为有很多个课程,学生学完了一个课程觉得好的话,以后还可以再报其它班级，
        # 每报一个班级,就得单独创建一条报名记录,所以这里想避免重复数据的话,就得搞个"客户 + 班级"的联合唯一喽


class CustomerFollowUp(models.Model):
    """存储客户的后续跟进信息"""
    customer = models.ForeignKey("Customer", verbose_name=u"所咨询客户", on_delete=models.CASCADE)
    note = models.TextField(u"跟进内容...")
    status_choices = ((1, u"近期无报名计划"),
                      (2, u"2个月内报名"),
                      (3, u"1个月内报名"),
                      (4, u"2周内报名"),
                      (5, u"1周内报名"),
                      (6, u"2天内报名"),
                      (7, u"已报名"),
                      (8, u"已交全款"),
                      )
    status = models.IntegerField(u"状态", choices=status_choices, help_text=u"选择客户此时的状态")

    consultant = models.ForeignKey("UserProfile", verbose_name=u"跟踪人", on_delete=models.CASCADE)
    date = models.DateField(u"跟进日期", auto_now_add=True)

    def __str__(self):
        return u"%s, %s" % (self.customer, self.status)

    class Meta:
        verbose_name = u'客户咨询跟进记录'
        verbose_name_plural = u"客户咨询跟进记录"


class ClassList(models.Model):
    """存储班级信息"""
    # 创建班级时需要选择这个班所学的课程
    branch = models.ForeignKey("Branch", verbose_name=u"校区", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", verbose_name=u"课程", on_delete=models.CASCADE)
    class_type_choices = ((0, '面授'), (1, '随到随学网络'))
    class_type = models.SmallIntegerField(choices=class_type_choices, default=0)
    total_class_nums = models.PositiveIntegerField("课程总节次", default=10)
    semester = models.IntegerField(u"学期")
    price = models.IntegerField(u"学费", default=10000)
    start_date = models.DateField(u"开班日期")
    graduate_date = models.DateField(u"结业日期", blank=True, null=True)
    # 选择这个班包括的讲师，可以是多个
    teachers = models.ManyToManyField("UserProfile", verbose_name=u"讲师")
    contract = models.ForeignKey("ContractTemplate", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s(%s)" % (self.course, self.semester)

    class Meta:
        verbose_name = u'班级列表'
        verbose_name_plural = u"班级列表"
        # 为避免重复创建班级,课程名＋学期做联合唯一
        unique_together = ("course", "semester")
    # 自定义方法，反向查找每个班级学员的数量，在后台admin里 list_display加上这个"get_student_num"就可以看到

    # def get_student_num(self):
    #     return "%s" % self.customer_set.select_related().count()
    #
    # get_student_num.short_description = u'学员数量'


class Course(models.Model):
    """存储所开设课程的信息"""
    name = models.CharField(u"课程名", max_length=64, unique=True)
    description = models.TextField(u"课程描述")
    outline = models.TextField(u"课程大纲")
    period = models.IntegerField(u"课程周期(Month)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = "课程"


class CourseRecord(models.Model):
    """存储各班级的上课记录"""
    # 讲师创建上课纪录时要选择是上哪个班的课
    from_class = models.ForeignKey("ClassList", verbose_name=u"班级(课程)", on_delete=models.CASCADE)
    day_num = models.IntegerField(u"节次", help_text=u"此处填写第几节课或第几天课程...,必须为数字")
    date = models.DateField(auto_now_add=True, verbose_name=u"上课日期")
    teacher = models.ForeignKey("UserProfile", verbose_name=u"讲师", on_delete=models.CASCADE)
    has_homework = models.BooleanField(default=True, verbose_name=u"本节有作业")
    homework_title = models.CharField(max_length=128, blank=True, null=True)
    homework_requirement = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s 第%s天" % (self.from_class, self.day_num)

    class Meta:
        verbose_name = '上课纪录'
        verbose_name_plural = "上课纪录"
        unique_together = ('from_class', 'day_num')


class StudyRecord(models.Model):
    """存储所有学员的详细的学习成绩,考勤情况"""
    student = models.ForeignKey("Enrollment", verbose_name=u"学员", on_delete=models.CASCADE)
    course_record = models.ForeignKey("CourseRecord", verbose_name=u"第几天课程", on_delete=models.CASCADE)
    record_choices = (('checked', u"已签到"),
                      ('late', u"迟到"),
                      ('noshow', u"缺勤"),
                      ('leave_early', u"早退"),
                      )
    attendance = models.CharField(u"上课纪录", choices=record_choices, default="checked", max_length=64)
    score_choices = ((100, 'A+'),   (90, 'A'),
                     (85, 'B+'),     (80, 'B'),
                     (70, 'B-'),     (60, 'C+'),
                     (50, 'C'),      (40, 'C-'),
                     (-50, 'D'),       (0, 'N/A'),
                     (-100, 'COPY'), (-1000, 'FAIL'),
                     )
    score = models.IntegerField(u"本节成绩", choices=score_choices, default=-1)
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(u"备注", max_length=255, blank=True, null=True)

    def __str__(self):
        return u"%s,学员:%s,纪录:%s, 成绩:%s" % (self.student, self.course_record, self.score, self.get_score_display())

    class Meta:
        verbose_name = u'学员学习纪录'
        verbose_name_plural = u"学员学习纪录"
        # 一个学员，在同一节课只可能出现一次，所以这里把course_record ＋ student 做成联合唯一
        unique_together = ('course_record', 'student')


class UserProfile(auth.AbstractBaseUser, auth.PermissionsMixin):  # 自定义验证
    # user = models.OneToOneField(User, on_delete=True)  # 使用Django自带的User表
    email = models.EmailField(
        verbose_name='邮箱地址',
        max_length=255,
        unique=True,
    )
    # password = models.CharField(_('password'), max_length=128,
    #                             help_text=mark_safe('''<a class='btn-link' href='password'>重置密码</a>'''))
    password = models.CharField(u"密码", max_length=128)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        verbose_name='staff status',
        default=True,
        help_text='Designates whether the user can log into this admin site.',
    )
    name = models.CharField(max_length=32, verbose_name="用户名")
    # role = models.ForeignKey("Role",verbose_name="权限角色")
    branch = models.ForeignKey("Branch", verbose_name="所属校区", blank=True, null=True, on_delete=models.CASCADE)
    roles = models.ManyToManyField('Role', verbose_name="角色")
    memo = models.TextField('备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    USERNAME_FIELD = 'email'  # 唯一标识
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perms(self, perm, obj=None):
        "Does the user have a specific permission?对哪些表"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    #
    #
    # @property
    # def is_superuser(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin
    #
    # class Meta:
    #     verbose_name = '用户信息'
    #     verbose_name_plural = u"用户信息"
    #
    #

    objects = auth.UserProfileManager()  # 创建用户

    @property
    def is_superuser(self):
        """不加这个报错"""
        return self.is_admin

    @property
    def is_staff(self):
        """是否运行user访问admin界面"""
        return self.is_active

    class Meta:
        verbose_name = 'CRM账户'
        verbose_name_plural = 'CRM账户'

        # # 权限为什么这么写?因为格式就是这样的,这个权限其实最好改成动态添加,由于时间关系,暂时放着
        # permissions = (
        #     ('easyadmin_customers', '可以访问 客户库'),
        #     ('easyadmin_table_list', '可以访问 easyadmin 每个表的数据列表页'),
        #     ('easyadmin_table_index', '可以访问 easyadmin 首页'),
        #     ('easyadmin_table_list_view', '可以访问 easyadmin 每个表中对象的修改页'),
        #     ('easyadmin_table_list_change', '可以修改 easyadmin 每个表中对象'),
        #     ('easyadmin_table_list_action', '可以操作 每个表的 action 功能'),
        #     ('easyadmin_can_access_my_clients', '可以访问 自己的 客户列表'),
        # )


class StuAccount(models.Model):
    """存储学员账户信息"""
    account = models.OneToOneField("Customer", on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    valid_start = models.DateTimeField("账户有效期开始", blank=True, null=True)
    valid_end = models.DateTimeField("账户有效期截止", blank=True, null=True)

    def __str__(self):
        return self.account.name

    class Meta:
        verbose_name = "学员账户"
        verbose_name_plural = "学员账户"


class Role(models.Model):
    """角色信息"""
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField('Menu', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"角色"
        verbose_name_plural = u"角色"


class Branch(models.Model):
    """存储所有校区"""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"校区"
        verbose_name_plural = u"校区"


class Menu(models.Model):
    """用于前端动态菜单"""
    name = models.CharField(unique=True, max_length=32)
    url_type = models.SmallIntegerField(
        choices=(
            (0, 'relative_name'),  # 对应views中函数的别名name
            (1, 'absolute_url')  # 对应url地址
        )
    )
    url_name = models.CharField(unique=True, max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "前端菜单"
        verbose_name_plural = "前端菜单"


class PaymentRecord(models.Model):
    """缴费记录"""
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    pay_type_choices = (('deposit', u"订金/报名费"),
                        ('tution', u"学费"),
                        ('refund', u"退款"),
                        )
    pay_type = models.CharField(u"费用类型", choices=pay_type_choices, max_length=64, default="deposit")
    paid_fee = models.IntegerField(u"费用数额", default=0)
    note = models.TextField(u"备注", blank=True, null=True)
    date = models.DateTimeField(u"交款日期", auto_now_add=True)
    consultant = models.ForeignKey(UserProfile, verbose_name=u"负责老师", help_text=u"谁签的单就选谁", on_delete=models.CASCADE)

    def __str__(self):
        return "%s, 类型:%s,数额:%s" % (self.enrollment.customer, self.pay_type, self.paid_fee)

    class Meta:
        verbose_name = '缴费纪录'
        verbose_name_plural = "缴费纪录"


class ContractTemplate(models.Model):
    """合同模板"""
    name = models.CharField("合同名称", max_length=64, unique=True)
    template = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "合同模板"
        verbose_name_plural = "合同模板"


class AdminPermission(models.Model):
    """
    管理员权限表
    """
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ManyToManyField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('easy_admin_main_pg', '可以访问管理员主页'),
            ('app_tables', '可以查看所有APP'),
            ('this_table', '可以查看具体表'),
            ('table_add', '可以添加表'),
            ('table_modify', '可以修改表'),
            ('table_delete', '可以删除表'),
        )


class TeacherPermission(models.Model):
    """
    讲师权限表
    """
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ManyToManyField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('teacher_main_pg', '可以访问讲师主页'),
            ('my_classes', '可以访问我的班级'),
            ('course_record', '可以访问上课记录'),
            ('view_class_stu_list', '可以访问学员列表'),
        )


class SalesPermission(models.Model):
    """
    销售权限表
    """
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ManyToManyField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('market_main_pg', '可以访问销售主页'),
            ('customers', '可以访问客户信息'),
            ('customer_modify', '可以修改客户信息'),
            ('enrollment', '可以访问帮助学员报名主页'),
            ('stu_enrollment', '可以查看学员报名表单模板'),
        )


class StudentPermission(models.Model):
    """
    销售权限表
    """
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ManyToManyField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('my_courses', '可以查看我的课程'),
            ('my_grade', '可以查看我的班级'),
            ('homework_detail', '可以查看作业信息'),
            ('delete_file', '可以删除作业'),
            ('my_homeworks', '可以提交作业'),
        )
