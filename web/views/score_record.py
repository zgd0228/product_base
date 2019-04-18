from django.conf.urls import url
from .base import PermissionHandle
from stark.service.v1 import StarkHandler,StarkModelForm
from web import models

class ScoreRecordModelForm(StarkModelForm):
    class Meta:
        model = models.ScoreRecord
        fields = ['content','score']


class ScoreRecordHandler(PermissionHandle,StarkHandler):

    def get_label_name(self,request,*args,**kwargs):
        '''
        为以后的扩展预留，根据不同的情况显示不同的内容（列）
        :return:
        '''
        value = []
        if self.label_name:
            value.extend(self.label_name)
        return value

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<student_id>\d+)/$', self.wrapper(self.list), name=self.get_list_url_name),
            url(r'^add/(?P<student_id>\d+)/$', self.wrapper(self.add),
                name=self.get_add_url_name),

        ]
        patterns.extend(self.extra_urls())
        return patterns
    def queryset_obj(self,request,*args,**kwargs):
        student_id = kwargs['student_id']
        return self.model_class.objects.filter(student_id=student_id)
    def save(self,request,form,is_update,*args,**kwargs):
        current_user_id = request.session['user']['id']
        student_id = kwargs['student_id']
        form.instance.student_id=student_id
        form.instance.user_id = current_user_id
        form.save()
        score = form.instance.score
        if score>0:
            form.instance.student.score += score
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()
    label_name = ['content','student','user']
    model_form_class = ScoreRecordModelForm