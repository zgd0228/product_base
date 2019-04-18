from django.conf.urls import url
from django.shortcuts import render,HttpResponse
from django.utils.safestring import mark_safe
from stark.service.v1 import StarkModelForm, StarkHandler
from web import models
from .base import PermissionHandle

class RecordModelForm(StarkModelForm):
    class Meta:
        model = models.Record
        fields = ['note']


class RecordHandler(PermissionHandle,StarkHandler):
    change_list_templates = 'record_view.html'

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.list), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add), name=self.get_add_url_name),
            url(r'^change/(?P<customer_id>\d+)/(?P<id>\d+)/$', self.wrapper(self.change),
                name=self.get_change_url_name),
            url(r'^delete/(?P<customer_id>\d+)/(?P<id>\d+)/$', self.wrapper(self.delete),
                name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def queryset_obj(self, request, *args, **kwargs):
        current_user_id = request.session['user']['id']
        customer_id = kwargs.get('customer_id')

        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def save(self, request, form, is_update, *args, **kwargs):

        current_user_id = request.session['user']['id']
        customer_id = kwargs['customer_id']
        customer_obj = models.Customer.objects.filter(id=customer_id,consultant_id=current_user_id)
        if not customer_obj.exists():
            return HttpResponse('非法操作')
        if not is_update:
            form.instance.customer_consultant_id = current_user_id
            form.instance.customer_id = customer_id
        form.save()

    def display_change(self, obj=None, is_header=None, *args, **kwargs):

        '''
        编辑按钮的url或者表头的编辑
        :param obj:
        :param is_header:
        :return:
        '''

        if is_header:
            return '编辑'
        name = self.reverse_change_url(id=obj.pk,customer_id = kwargs['customer_id'])

        return mark_safe("<a href='%s'>编辑</a>" % name)

    def display_delete(self, obj=None, is_header=None, *args, **kwargs):
        '''
        删除按钮的url
        :param obj:
        :param is_header:
        :return:
        '''
        if is_header:
            return '删除'
        name = self.reverse_delete_url(id=obj.pk,customer_id = kwargs['customer_id'])
        return mark_safe("<a href='%s'>删除</a>" %name )

    def get_change_object(self,request,id,*args,**kwargs):
        current_user_id = request.session['user']['id']
        customer_id = kwargs['customer_id']
        change_query = self.model_class.objects.filter(id=id,customer_id=customer_id,
                                                       customer__consultant_id = current_user_id)
        return change_query.first()

    def delete_object(self,request,id,*args,**kwargs):
        current_user_id = request.session['user']['id']
        customer_id = kwargs['customer_id']
        delete_query = self.model_class.objects.filter(id=id,customer_id=customer_id,
                                                       customer__consultant_id = current_user_id)
        if not delete_query:

            return HttpResponse('删除的记录不存在，请重新输入')
        delete_query.delete()

    label_name = ['customer_consultant', 'date', 'note']
    model_form_class = RecordModelForm
