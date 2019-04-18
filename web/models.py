from django.db import models
from rbac.models import UserInfo as RbacUserInfo
# Create your models here.

# 如果说缴费的额度与课程的费用不相等，是不可以缴费成功的

class School(models.Model):
    '''

    '''
    title = models.CharField(verbose_name='校区名称',max_length=32)

    def __str__(self):
        return self.title

class Depart(models.Model):
    '''

    '''
    title = models.CharField(verbose_name='部门',max_length=32)

    def __str__(self):
        return self.title

class UserInfo(RbacUserInfo):

    realname = models.CharField(max_length=32,verbose_name='姓名')
    phone = models.CharField(max_length=32,verbose_name='电话')

    gender_choices = (
        (1,'男'),
        (2,'女')
    )
    gender = models.IntegerField(verbose_name='性别',choices=gender_choices)
    depart = models.ForeignKey(to='Depart',verbose_name='部门')
    # school = models.ForeignKey(to='School',verbose_name='校区')

    def __str__(self):
        return self.realname

class Course(models.Model):

    title = models.CharField(verbose_name='课程名称',max_length=32)

    def __str__(self):
        return self.title

class ClassList(models.Model):

    school = models.ForeignKey(to='School',verbose_name='校区')
    teach_teacher = models.ManyToManyField(to='UserInfo',verbose_name='教师',related_name='each_classes',
                                           limit_choices_to={'depart__title__in':['python教学部','linux教学部','爬虫']},blank=True)
    manage_teacher = models.ForeignKey(to='UserInfo',verbose_name='班主任',related_name='classes',
                                       limit_choices_to={'depart__title':'运营部'})
    start_date = models.DateField(verbose_name='开班日期',)
    graduate_date = models.DateField(verbose_name='结业日期',blank=True,null=True)
    price = models.PositiveIntegerField(verbose_name='学费')
    course = models.ForeignKey(to='Course',verbose_name='课程')
    period = models.PositiveIntegerField(verbose_name='期')
    memo = models.TextField(verbose_name='说明',blank=True)

    def __str__(self):
        return '{0}({1}期)'.format(self.course.title,self.period)


class Customer(models.Model):
    qq = models.CharField(verbose_name='联系方式',max_length=32,unique=True)

    name = models.CharField(verbose_name='客户姓名',max_length=32)
    statue_choices = (
        (1,'已报名'),
        (2,'未报名')
    )
    status = models.IntegerField(verbose_name='状态',default=2,choices=statue_choices,help_text='报名状态')
    gender_choices = (
        (1,'女'),
        (2,'男')
    )
    gender = models.IntegerField(verbose_name='性别',choices=gender_choices,default=2)

    work_state_choices=(
        (1,'在职'),
        (2,'无业')
    )
    work_state = models.IntegerField(verbose_name='工作状态',choices=work_state_choices)
    source_choices = (
        (1, "qq群"),
        (2, "内部转介绍"),
        (3, "官方网站"),
        (4, "百度推广"),
        (5, "360推广"),
        (6, "搜狗推广"),
        (7, "腾讯课堂"),
        (8, "广点通"),
        (9, "高校宣讲"),
        (10, "渠道代理"),
        (11, "51cto"),
        (12, "智汇推"),
        (13, "网盟"),
        (14, "DSP"),
        (15, "SEO"),
        (16, "其它"),
    )
    source = models.SmallIntegerField('客户来源', choices=source_choices, default=1)
    course = models.ManyToManyField(verbose_name="咨询课程", to="Course")
    consultant = models.ForeignKey(verbose_name="课程顾问", to='UserInfo', related_name='consultant',
                                   null=True, blank=True,
                                   limit_choices_to={'depart__title': '销售部'})
    education_choices = (
        (1, '重点大学'),
        (2, '普通本科'),
        (3, '独立院校'),
        (4, '民办本科'),
        (5, '大专'),
        (6, '民办专科'),
        (7, '高中'),
        (8, '其他')
    )
    education = models.IntegerField(verbose_name='学历', choices=education_choices, blank=True, null=True, )
    graduation_school = models.CharField(verbose_name='毕业学校', max_length=64, blank=True, null=True)
    major = models.CharField(verbose_name='所学专业', max_length=64, blank=True, null=True)
    referral_from = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        verbose_name="转介绍自学员",
        help_text="若此客户是转介绍自内部学员,请在此处选择内部学员姓名",
        related_name="internal_referral"
    )
    experience_choices=(
        (1,'在校生'),
        (2,'应届毕业'),
        (3,'半年以内'),
        (4,'半年至一年'),
        (5,'一年至三年'),
        (6,'三年至五年'),
        (7,'五年以上')
    )
    experience = models.IntegerField(verbose_name='工作经验',choices=experience_choices)
    salary = models.CharField(verbose_name='目前薪资',blank=True,null=True,max_length=32)
    company = models.CharField(verbose_name='在职公司',blank=True,null=True,max_length=32)
    date = models.DateField(verbose_name='咨询时间',auto_now_add=True)
    last_consult_date = models.DateField(verbose_name='最后跟进时间',auto_now_add=True)


    def __str__(self):
        return "姓名:{0},联系方式:{1}".format(self.name, self.qq, )

class Record(models.Model):
    date = models.DateField(verbose_name='跟进日期',auto_now_add=True)
    note = models.TextField(verbose_name='跟进内容')
    customer = models.ForeignKey(to='Customer',verbose_name='跟进客户')
    customer_consultant = models.ForeignKey(to='UserInfo',verbose_name='跟进人')


class PaymentRecord(models.Model):
    """
    缴费申请
    """
    customer = models.ForeignKey(Customer, verbose_name="客户")
    consultant = models.ForeignKey(verbose_name="课程顾问", to='UserInfo', help_text="谁签的单就选谁")
    pay_type_choices = [
        (1, "报名费"),
        (2, "学费"),
        (3, "退学"),
        (4, "其他"),
    ]
    pay_type = models.IntegerField(verbose_name="费用类型", choices=pay_type_choices, default=1)
    paid_fee = models.IntegerField(verbose_name="金额", default=0)
    class_list = models.ForeignKey(verbose_name="申请班级", to="ClassList")
    apply_date = models.DateTimeField(verbose_name="申请日期", auto_now_add=True)

    confirm_status_choices = (
        (1, '申请中'),
        (2, '已确认'),
        (3, '已驳回'),
    )
    confirm_status = models.IntegerField(verbose_name="确认状态", choices=confirm_status_choices, default=1)
    confirm_date = models.DateTimeField(verbose_name="确认日期", null=True, blank=True)
    confirm_user = models.ForeignKey(verbose_name="审批人", to='UserInfo', related_name='confirms', null=True, blank=True)

    note = models.TextField(verbose_name="备注", blank=True, null=True)

    def __str__(self):
        return self.customer.name


class Student(models.Model):
    """
    学生表
    """
    customer = models.OneToOneField(verbose_name='客户信息', to='Customer')
    qq = models.CharField(verbose_name='QQ号', max_length=32)
    mobile = models.CharField(verbose_name='手机号', max_length=32)
    emergency_contract = models.CharField(verbose_name='紧急联系人电话', max_length=32)
    score = models.IntegerField(verbose_name='积分', default=100)
    class_list = models.ManyToManyField(verbose_name="已报班级", to='ClassList', blank=True)
    student_status_choices = [
        (1, "申请中"),
        (2, "在读"),
        (3, "毕业"),
        (4, "退学")
    ]
    student_status = models.IntegerField(verbose_name="学员状态", choices=student_status_choices, default=1)
    memo = models.TextField(verbose_name='备注', max_length=255, blank=True, null=True)

    def __str__(self):
        return self.customer.name


class ScoreRecord(models.Model):
    """
    积分记录
    """
    student = models.ForeignKey(verbose_name='学生', to='Student')
    content = models.TextField(verbose_name='理由')
    score = models.IntegerField(verbose_name='分值', help_text='违纪扣分写负值，表现邮寄加分写正值')
    user = models.ForeignKey(verbose_name='执行人', to='UserInfo')


class CourseRecord(models.Model):
    """
    上课记录表
    """
    class_object = models.ForeignKey(verbose_name="班级", to="ClassList")
    day_num = models.IntegerField(verbose_name="节次")
    teacher = models.ForeignKey(verbose_name="讲师", to='UserInfo',
                                limit_choices_to={'depart__title__in':['python教学部','linux教学部','爬虫']})
    date = models.DateField(verbose_name="上课日期", auto_now_add=True)

    def __str__(self):
        return "{0} day{1}".format(self.class_object, self.day_num)


class StudyRecord(models.Model):
    """
    学生考勤记录
    """
    course_record = models.ForeignKey(verbose_name="第几天课程", to="CourseRecord")
    student = models.ForeignKey(verbose_name="学员", to='Student')
    record_choices = (
        ('checked', "已签到"),
        ('vacate', "请假"),
        ('late', "迟到"),
        ('noshow', "缺勤"),
        ('leave_early', "早退"),
    )
    record = models.CharField("上课纪录", choices=record_choices, default="checked", max_length=64)












