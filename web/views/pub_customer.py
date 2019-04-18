from django.conf.urls import url
from django.shortcuts import HttpResponse,render
from django.utils.safestring import mark_safe
from django.db import transaction
from stark.service.v1 import StarkHandler,StarkModelForm,get_choice_text,get_mtom_text
from web import models
from .base import PermissionHandle

class PublishCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        # fields = '__all__'
        exclude = ['consultant']

class PublishCustomerHandler(PermissionHandle,StarkHandler):
    MAX_CUSTOMER = 150
    def display_record(self,obj=None,is_header=None):
        if is_header:
            return '跟进详情'
        reverse_record = self.reverse_common_url(self.get_url_name('record'),id=obj.pk)
        return mark_safe("<a href='%s'>跟进记录</a>"%reverse_record)

    def record(self,request,id,*args,**kwargs):
        form = models.Record.objects.filter(customer_id=id)

        return render(request,'record_list.html',locals())

    def extra_urls(self):
        patterns = [
            url(r'record/(?P<id>\d+)/$',self.wrapper(self.record),name=self.get_url_name('record')),
        ]
        return patterns

    def queryset_obj(self,request,*args,**kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    label_name = [StarkHandler.display_checkbox,'name','qq',get_mtom_text('咨询课程','course'),get_choice_text('状态','status'),display_record]

    def multi_public(self,request):
        current_user_id = request.session['user']['id']
        pk_list = request.POST.getlist('pk')
        has_customer_count = self.model_class.objects.filter(consultant_id=current_user_id,status=2).count()
        # 私户个数限制
        if (len(pk_list)+has_customer_count) > self.MAX_CUSTOMER:
            return HttpResponse('你的私户中已有%s个客户，最多只能申请%s个客户'%(has_customer_count,
                                                         (self.MAX_CUSTOMER-has_customer_count)))
        flag = False
        with transaction.atomic():
            origin_queryset = self.model_class.objects.filter(id__in=pk_list,
                        consultant__isnull=True,status=2).select_for_update()

            if len(origin_queryset) == len(pk_list):
                self.model_class.objects.filter(id__in=pk_list,consultant__isnull=True,
                                               status=2).update(consultant_id=current_user_id)
                flag = True
        if not flag:
            return HttpResponse('选中的客户已被其他人申请，请重新选择')

    multi_public.text = '添加到私户'
    action_list = [multi_public]
    model_form_class = PublishCustomerModelForm