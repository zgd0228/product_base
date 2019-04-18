from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.urls import reverse
from web import models
from .base import PermissionHandle

from stark.service.v1 import StarkHandler,get_choice_text,get_mtom_text,StarkModelForm,Option

class StudentModelForm(StarkModelForm):
    class Meta:
        model = models.Student
        fields = ['qq','mobile','emergency_contract','memo']

class StudentHandler(PermissionHandle,StarkHandler):

    def display_score(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return '积分管理'
        score_url = reverse('stark:web_scorerecord_list',kwargs={'student_id':obj.pk})

        return mark_safe('<a href="%s">%s</a>'%(score_url,obj.score))

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.list), name=self.get_list_url_name),
            url(r'^change/(?P<id>\d+)/$', self.wrapper(self.change),
                name=self.get_change_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_label_name(self,request,*args,**kwargs):
        '''
        为以后的扩展预留，根据不同的情况显示不同的内容（列）
        :return:
        '''
        value = []
        value.extend(self.label_name)
        if self.label_name:
            value.append(type(self).display_change)
        return value
    has_add_btn = False
    label_name = ['customer','qq','mobile','emergency_contract',get_mtom_text('班级','class_list'),
                  get_choice_text('状态','student_status'),display_score]
    search_list = ['customer__name','qq','mobile']

    search_group = [Option('class_list',text_func=lambda x:'%s-%s'%(x.school.title,str(x)))]
    model_form_class = StudentModelForm
