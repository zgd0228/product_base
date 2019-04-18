import functools
import datetime
from types import FunctionType
from django.shortcuts import HttpResponse,render,redirect
from django.conf.urls import url
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import QueryDict
from django.forms import ModelForm
from django import forms
from django.db.models import Q
from django.db.models import ForeignKey,ManyToManyField
from django.core.exceptions import ValidationError
from stark.page.Page import Pagination
from web.utils.md5 import hash_md5

def get_choice_text(title,field,*args,**kwargs):
    '''
    对于表中有选择的字段显示中文
    :param title: 表头名称
    :param field: 表的字段
    :return:
    '''
    def inner(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return title
        method = 'get_%s_display'%field
        return getattr(obj,method)
    return inner

def get_date_text(title,field,format='%Y-%m-%d',*args,**kwargs):
    '''

    :param title:
    :param field:
    :param format:
    :return:
    '''
    def inner(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return title
        datetime_value = getattr(obj,field)
        return datetime_value.strftime(format)
    return inner

def get_mtom_text(title,field,*args,**kwargs):
    '''
    manytomany字段的内容展示
    :param title:
    :param field:
    :return:
    '''
    def inner(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return title
        queryset = getattr(obj,field).all()
        text_list = [str(item) for item in queryset]
        return ' , '.join(text_list)
    return inner

class StarkModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StarkModelForm, self).__init__(*args, **kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class StarkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ResetPwdModelForm(StarkForm):

    pwd = forms.CharField(label='密码',widget=forms.PasswordInput)
    confirm_pwd = forms.CharField(label='确认密码',widget=forms.PasswordInput)

    def clean_confirm_pwd(self):  # 一定一定要注意的是钩子名称要带clean，和字段名称，要一模一杨
        pwd = self.cleaned_data['pwd']
        confirm_pwd = self.cleaned_data['confirm_pwd']
        if pwd != confirm_pwd:
            raise ValidationError('两次输入的密码不一致')
        return confirm_pwd

    def clean(self):
        pwd = self.cleaned_data['pwd']
        self.cleaned_data['pwd'] = hash_md5(pwd)
        return self.cleaned_data

class Option(object):
    def __init__(self,field,is_multi=False,db_condition=None,text_func=None,text_func_value=None):
        '''
        批量操作（组合搜素）
        :param field:组合搜索字段
        :param is_multi:
        :param db_condition:条件
        :param text_func:
        :param text_func_value:
        :return:
        '''
        self.field = field
        self.is_multi = is_multi
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.text_func_value = text_func_value
        self.is_choice = False

    def get_db_condition(self,request,*args,**kwargs):
        '''
        预留数据库查询条件扩展接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        return self.db_condition

    def get_queryset_or_tuple(self,model_class,request,*args,**kwargs):
        '''

        :param model_class:
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        group_obj = model_class._meta.get_field(self.field)
        title = group_obj.verbose_name

        if isinstance(group_obj,ForeignKey) or isinstance(group_obj,ManyToManyField):
            db_condition = self.get_db_condition(request,*args,**kwargs)
            db_field = group_obj.rel.model.objects.filter(**db_condition)
            return GroupRow(title,db_field,self,request.GET)
        else:
            choices = group_obj.choices
            self.is_choice = True
            return GroupRow(title,choices,self,request.GET)

    def get_text_func(self,field_obj):
        if self.text_func:
            return self.text_func(field_obj)
        if self.is_choice:
            return field_obj[1]
        return str(field_obj)

    def get_text_value(self,field_obj):
        if self.text_func_value:
            return self.text_func_value(field_obj)
        if self.is_choice:
            return field_obj[0]
        return field_obj.pk

class GroupRow(object):
    def __init__(self,title,queryset_or_tuple,option,query_dict):
        self.title = title
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.query_dict = query_dict

    def __iter__(self):
        yield '<div class="whole_title">'
        yield self.title+':'
        yield '</div>'
        yield '<div class="whole">'
        total_query_dict = self.query_dict.copy()
        total_query_dict._mutable = True
        origin_value_list = self.query_dict.getlist(self.option.field)
        if not origin_value_list:
            yield '<a class="active" href="?%s">全部</a>'%(total_query_dict.urlencode())
        else:
            # print(self.option.field)     #   这里还需要仔细考虑
            total_query_dict.pop(self.option.field)
            yield '<a href="?%s">全部</a>'%(total_query_dict.urlencode())
        yield '</div>'
        yield '<div class="others">'
        for item in self.queryset_or_tuple:
            value = str(self.option.get_text_value(item))
            text = self.option.get_text_func(item)
            query_dict = self.query_dict.copy()
            query_dict._mutable = True
            query_dict[self.option.field] = value
            if not self.option.is_multi:
                if value in origin_value_list:
                    query_dict.pop(self.option.field)
                    yield '<a class="active" href="?%s">%s</a>'%(query_dict.urlencode(),text)
                else:
                    yield '<a href="?%s">%s</a>'%(query_dict.urlencode(),text)
            else:
                multi_list = self.query_dict.getlist(self.option.field)
                if value in multi_list:
                    multi_list.remove(value)
                    query_dict.setlist(self.option.field,multi_list)
                    yield '<a class="active" href="?%s">%s</a>'%(query_dict.urlencode(),text)
                else:
                    multi_list.append(value)
                    query_dict.setlist(self.option.field,multi_list)
                    yield '<a href="?%s">%s</a>'%(query_dict.urlencode(),text)
        yield '</div>'

class StarkSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self,model_class,handler=None,prev=None):
        '''

        :param model_class:数据库中的class，如model.UserInfo
        :param handler:路由视图处理函数的类
        :param prev:前缀
        :return:
        '''
        if not handler:
            handler = StarkHandler
        self._registry.append({'model_class':model_class,'handler':handler(model_class,prev,site),'prev':prev})

    def get_urls(self):
        '''

        :return:
        '''
        patterns = []
        for item in self._registry:
            model_class = item['model_class']
            handler = item['handler']
            prev = item['prev']
            app_label,model_name = model_class._meta.app_label,model_class._meta.model_name
            if prev:
                patterns.append(url(r'%s/%s/%s/'%(app_label,model_name,prev),(handler.get_urls(),None,None)))
            else:
                patterns.append(url(r'%s/%s/'%(app_label,model_name),(handler.get_urls(),None,None)))
        return patterns
    @property
    def urls(self):
        return self.get_urls(),self.app_name,self.namespace

class StarkHandler(object):

    def __init__(self,model_class,prev,site,):
        self.model_class = model_class
        self.prev = prev
        self.site = site
        self.request = None

    has_add_btn = True

    model_form_class = None

    label_name = []  #字段

    order_list = []   #排序

    search_list = []   # 搜索

    action_list = []  #批量操作

    search_group = []   #组合搜索

    change_list_templates = None

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '操作'

        tpl = '<a href="%s">编辑</a> <a href="%s">删除</a>' % (
            self.reverse_change_url(id=obj.pk), self.reverse_delete_url(id=obj.pk))
        return mark_safe(tpl)

    def get_model_form_class(self,request,is_add=False,*args,**kwargs):
        '''
        获取modelform，并且为每一个字段定制样式
        :return:
        '''
        if self.model_form_class:
            return self.model_form_class
        class ChangeForm(StarkModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'
        return ChangeForm

    def get_action_list(self,):
        '''
        获取批量操作列表
        :return:
        '''
        return self.action_list

    def multi_init(self,request,*args,**kwargs):
        pass

    def multi_delete(self,request,*args,**kwargs):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()

    multi_init.text = '批量初始化'
    multi_delete.text = '批量删除'

    def get_order_list(self):
        '''
        排序
        :return:
        '''
        return self.order_list or ['id']

    def get_search_list(self):
        '''
        搜索
        :return:
        '''
        # return self.search_list or ['name','title']
        return self.search_list

    def get_search_group(self):
        '''
        组合搜索
        :return:
        '''
        return self.search_group

    def get_add_btn(self,request,*args,**kwargs):
        '''
        添加按钮
        :return:
        '''

        if self.has_add_btn:
            return "<a class='btn btn-success' href='%s'>添加</a>"%self.reverse_add_url(*args,**kwargs)
        return None

    def get_label_name(self,request,*args,**kwargs):
        '''
        为以后的扩展预留，根据不同的情况显示不同的内容（列）
        :return:
        '''
        value = []
        value.extend(self.label_name)
        if self.label_name:
            value.append(type(self).display_change)
            value.append(type(self).display_delete)

        return value

    def display_change(self,obj=None,is_header=None,*args,**kwargs):
        '''
        编辑按钮的url或者表头的编辑
        :param obj:
        :param is_header:
        :return:
        '''
        if is_header:
            return '编辑'
        name = self.reverse_change_url(id=obj.pk,*args,**kwargs)
        return mark_safe("<a href='%s'>编辑</a>"%name)

    def display_delete(self,obj=None,is_header=None,*args,**kwargs):
        '''
        删除按钮的url
        :param obj:
        :param is_header:
        :return:
        '''
        if is_header:
            return '删除'

        return mark_safe("<a href='%s'>删除</a>"%self.reverse_delete_url(id=obj.pk))

    def display_checkbox(self,obj=None,is_header=None,*args,**kwargs):
        '''
        批量操作选择框的表头与url的设置
        :param obj:
        :param is_header:
        :return:
        '''
        if is_header:
            return '选择'

        return mark_safe('<input type="checkbox" name="pk" value="%s">'%obj.pk)

    def display_reset_pwd(self,obj=None,is_header=None):
        if is_header:
            return '重置密码'
        return mark_safe('<a href="%s">重置密码</a>'%self.reverse_reset_pwd_url(id=obj.pk))

    def get_search_group_value(self,request):
        '''
        组合搜索的值
        :param request:
        :return:
        '''
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:
                value_list = request.GET.getlist(option.field)
                if not value_list:
                    continue
                condition['%s__in'%option.field] = value_list
            else:
                value = request.GET.get(option.field)
                if not value:
                    continue
                condition[option.field] = value
        return condition

    def queryset_obj(self,request,*args,**kwargs):

        return self.model_class.objects

    def list(self,request,*args,**kwargs):
        '''
        列表页面
        :return:
        '''

        order_list = self.get_order_list()  # 获取排序条件列表

        #搜索
        search_list = self.get_search_list()  # 获取搜索条件列表，是按照模糊搜索还是精确搜索
        conn = Q()
        conn.connector = 'OR'
        search_value = request.GET.get('q','')

        if search_value:
            for item in search_list:
                conn.children.append((item,search_value))

        # 批量操作
        action_list = self.get_action_list()
        action_dict = {}
        if action_list:
            for item in action_list:
                action_dict[item.__name__] = item.text
        if request.method == "POST":
            action_func_name = request.POST.get('action')
            if action_func_name and action_func_name in action_dict:
                getattr(self,action_func_name)(request,*args,**kwargs)

        search_group_condition = self.get_search_group_value(request)
        # 分页
        queryset_obj = self.queryset_obj(request,*args,**kwargs)
        queryset = queryset_obj.filter(conn).filter(**search_group_condition).order_by(*order_list)
        all_count = queryset.count()
        query_params = request.GET.copy()  # 获取GET内容，并将其拷贝，
        query_params._mutable = True  # 设置GET内容可以被修改
        pagination = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            query_params=query_params,
            base_url=request.path_info,
            per_page=10,
        )

        data_list = queryset[ pagination.start:pagination.end ]

        # 表头处理
        head_name = []   # 表头内容存放列表 eg:[name,age,email,...]
        label_name = self.get_label_name(request,*args,**kwargs)
        if label_name: # 判断是否存在表头内容，如果不存在则在列表中添加表名称
            for item in label_name:
                if isinstance(item,FunctionType):
                    verbose_name = item(self,obj=None,is_header=True,*args,**kwargs)
                else:
                    verbose_name = self.model_class._meta.get_field(item).verbose_name
                head_name.append(verbose_name)
        else:
            head_name.append(self.model_class._meta.model_name)

        # 表的内容处理
        body_list = []  # 表的内容，如[[zgd,18,xxx],[][]]

        for data in data_list:
            row_list = []
            if label_name:   # 判断是否存在表头内容，如果不存在则在列表中添加表对象
                for row in label_name:
                    if isinstance(row,FunctionType):
                        row_list.append(row(self,obj=data,*args,**kwargs))
                    else:
                        row_list.append(getattr(data,row))
            else:
                row_list.append(data)
            body_list.append(row_list)
        # 添加按钮
        add_btn = self.get_add_btn(request,*args,**kwargs)

        # 组合搜索
        search_group = self.get_search_group()
        search_group_list = []

        for option_obj in search_group:
            row = option_obj.get_queryset_or_tuple(self.model_class,request,*args,**kwargs)
            search_group_list.append(row)

        return render(request,
                      self.change_list_templates or 'stark/list.html',locals())

    def add(self,request,*args,**kwargs):
        '''
        添加页面
        :return:
        '''
        model_form_class = self.get_model_form_class(request,is_add=True,*args,**kwargs)
        if request.method == 'GET':
            form = model_form_class()
            return render(request,'stark/change.html',locals())
        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.save(request,form,False,*args,**kwargs)
            return response or redirect(self.reverse_list_url(*args,**kwargs))
        return render(request,'stark/change.html',locals())

    def get_change_object(self,request,id,*args,**kwargs):

        return self.model_class.objects.filter(id=id).first()

    def change(self,request,id,*args,**kwargs):
        '''
        编辑页面
        :return:
        '''
        current_object_data = self.get_change_object(request,id=id,*args,**kwargs)
        if not current_object_data:
            return HttpResponse('该用户或修改的数据不存在，请重新选择')
        model_form_class = self.get_model_form_class(request,is_add=False,*args,**kwargs)
        if request.method == 'GET':
            form = model_form_class(instance=current_object_data)
            return render(request,'stark/change.html',locals())
        form = model_form_class(data=self.request.POST,instance=current_object_data)
        if form.is_valid():
            response = self.save(request,form,True,*args,**kwargs)
            return response or redirect(self.reverse_list_url(*args,**kwargs))
        return render(request,'stark/change.html',locals())

    def delete_object(self,request,id,*args,**kwargs):

        self.model_class.objects.filter(id=id).delete()

    def delete(self,request,id,*args,**kwargs):
        '''
        删除页面
        :return:
        '''
        original_url = self.reverse_list_url(*args,**kwargs)
        if request.method == "GET":
            return render(request,'stark/delete.html',{'cancel':original_url})
        response = self.delete_object(request,id=id,*args,**kwargs)
        return response or redirect(original_url)

    def reset_pwd(self,request,id,*args,**kwargs):
        '''

        :param request:
        :param id:
        :param args:
        :param kwargs:
        :return:
        '''
        user_obj = self.model_class.objects.filter(id=id).first()
        if not user_obj:
            return HttpResponse('用户不存在')
        if request.method == 'GET':
            form = ResetPwdModelForm()
            return render(request,'stark/change.html',locals())
        form = ResetPwdModelForm(data=request.POST)
        if form.is_valid():
            user_obj.pwd = form.cleaned_data['pwd']
            user_obj.save()
            return redirect(self.reverse_list_url(*args,**kwargs))
        return render(request,'stark/change.html',locals())

    def get_url_name(self,param,*args,**kwargs):
        app_label,model_name = self.model_class._meta.app_label,self.model_class._meta.model_name
        if self.prev:
            return '%s_%s_%s_%s'%(app_label,model_name,self.prev,param)
        return '%s_%s_%s'%(app_label,model_name,param)

    def reverse_list_url(self,*args,**kwargs):
        '''
        反向生成list页面的url
        :return:
        '''
        name = '%s:%s'%(self.site.namespace,self.get_list_url_name)

        base_url = reverse(name,args=args,kwargs=kwargs)

        param = self.request.GET.get('_filter')
        if not param:
            return base_url
        return '%s?%s'%(base_url,param)

    def reverse_common_url(self,url_name,*args,**kwargs):
        '''

        :param url_name:
        :param args:
        :param kwargs:
        :return:
        '''
        name = '%s:%s'%(self.site.namespace,url_name)

        base_url = reverse(name, args=args, kwargs=kwargs)

        if not self.request.GET:
            add_url = base_url
        else:
            param = self.request.GET.urlencode()
            query_dict = QueryDict(mutable=True)
            query_dict['_filter'] = param
            add_url = '%s?%s'%(base_url,query_dict.urlencode())
        return add_url

    def reverse_add_url(self,*args,**kwargs):
        '''
        反向生成添加按钮的url
        :return:
        '''
        return self.reverse_common_url(self.get_add_url_name,*args,**kwargs)

    def reverse_change_url(self,*args,**kwargs):
        '''
        反向生成带原搜索条件的编辑url
        :return:
        '''
        return self.reverse_common_url(self.get_change_url_name,*args,**kwargs)

    def reverse_delete_url(self,*args,**kwargs):
        '''
        反向生成带原搜索条件的删除url
        :return:
        '''
        return self.reverse_common_url(self.get_delete_url_name,*args,**kwargs)

    def reverse_reset_pwd_url(self,*args,**kwargs):
        '''
        反向生成重置密码url
        :param args:
        :param kwargs:
        :return:
        '''
        return self.reverse_common_url(self.get_reset_pwd_url_name,*args,**kwargs)

    def wrapper(self,func):
        '''
        为方法获取request方法
        :param func:视图函数
        :return:
        '''
        @functools.wraps(func)   # 保留原函数的原信息
        def inner(request,*args,**kwargs):
            self.request = request
            return func(request,*args,**kwargs)
        return inner

    def save(self,request,form,is_update,*args,**kwargs):
        '''
        预留form.save()钩子，可以在外面重新定义
        :param form:
        :param is_update:
        :return:
        '''
        form.save()

    @property
    def get_list_url_name(self):
        '''
        获取显示页面的url别名
        :return:
        '''
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        '''
        获取添加页面的url别名
        :return:
        '''
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        '''
        获取编辑页面的url别名
        :return:
        '''
        return self.get_url_name('change')

    @property
    def get_delete_url_name(self):
        '''
        获取删除页面的url别名
        :return:
        '''
        return self.get_url_name('delete')

    @property
    def get_reset_pwd_url_name(self):
        '''
        获取重置密码url别名
        :return:
        '''
        return self.get_url_name('reset_pwd')

    def get_urls(self):
        '''
        路由分发
        :return:
        '''
        patterns = [
            url(r'list/$',self.wrapper(self.list),name=self.get_list_url_name),
            url(r'add/$',self.wrapper(self.add),name=self.get_add_url_name),
            url(r'change/(?P<id>\d+)/$',self.wrapper(self.change),name=self.get_change_url_name),
            url(r'delete/(?P<id>\d+)/$',self.wrapper(self.delete),name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def extra_urls(self):
        '''
        路由进一步分发钩子
        :return:
        '''
        return []

site = StarkSite()