from django import forms
from django.core.exceptions import ValidationError
from django.conf.urls import url
from web.utils.md5 import hash_md5
from web import models
from stark.service.v1 import site,StarkHandler,StarkModelForm,get_choice_text,Option
from .base import PermissionHandle

class UserInfoAddModelForm(PermissionHandle,StarkModelForm):
    confirm_pwd = forms.CharField(label='确认密码',widget=forms.PasswordInput)
    class Meta:
        model = models.UserInfo
        fields = ['realname','name','pwd','confirm_pwd','email','phone','depart','gender','roles']

    def __init__(self,*args,**kwargs):
        #统一给ModeForm生成的input添加样式
        super(UserInfoAddModelForm,self).__init__(*args,**kwargs)
        for name,field in self.fields.items():
            if name in ['pwd','confirm_pwd']:
                widgets = {name:forms.PasswordInput}


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

class UserInfoChangeModelForm(StarkModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name','realname','email','phone','depart','gender','roles']

class UserInfoHandler(StarkHandler):
    label_name = ['realname',get_choice_text('性别','gender'),'phone','email','depart',StarkHandler.display_reset_pwd]
    search_list = ['realname__contains']
    search_group = [Option('gender',is_multi=False),Option('depart',is_multi=False)]
    def get_model_form_class(self,request,is_add=False,*args,**kwargs):
        if is_add:
            return UserInfoAddModelForm
        return UserInfoChangeModelForm
    def extra_urls(self):
        patterns = [
            url(r'reset/pwd/(?P<id>\d+)/$',self.wrapper(self.reset_pwd),name=self.get_reset_pwd_url_name),
        ]
        return patterns