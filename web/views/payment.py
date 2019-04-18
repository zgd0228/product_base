from django.conf.urls import url
from django import forms
from django.shortcuts import render,HttpResponse
from django.utils.safestring import mark_safe
from stark.service.v1 import StarkModelForm, StarkHandler,get_choice_text,get_date_text
from web import models
from .base import PermissionHandle

class PaymentModelForm(StarkModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'note']

class PaymentStudentModelForm(StarkModelForm):
    qq = forms.CharField(label='QQ号')
    mobile = forms.CharField(label='手机号')
    emergency_contract = forms.CharField(label='紧急联系人电话')
    class Meta:
        model = models.PaymentRecord
        fields = ['qq','mobile','emergency_contract','pay_type', 'paid_fee', 'class_list', 'note']

class PaymentHandler(PermissionHandle,StarkHandler):

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.list), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def queryset_obj(self, request, *args, **kwargs):
        current_user_id = request.session['user']['id']
        customer_id = kwargs.get('customer_id')

        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def get_label_name(self,request,*args,**kwargs):
        '''
        为以后的扩展预留，根据不同的情况显示不同的内容（列）
        :return:
        '''
        value = []
        if self.label_name:
            value.extend(self.label_name)
        return value

    def get_model_form_class(self,request,is_add=False,*args,**kwargs):

        customer_id = kwargs.get('customer_id')
        student_exists = models.Student.objects.filter(customer_id=customer_id).exists()
        if student_exists:
            return PaymentModelForm
        return PaymentStudentModelForm

    def save(self,request,form,is_update,*args,**kwargs):
        current_user_id = request.session['user']['id']
        customer_id = kwargs.get('customer_id')
        customer_obj = models.Customer.objects.filter(id=customer_id,consultant_id=current_user_id)
        if not customer_obj.exists():
            return HttpResponse('非法操作')
        if not is_update:
            form.instance.consultant_id = current_user_id
            form.instance.customer_id = customer_id

        form.save()
        class_list = form.cleaned_data['class_list']
        student_object = models.Student.objects.filter(customer_id=customer_id).first()
        if not student_object:
            qq = form.cleaned_data['qq']
            mobile = form.cleaned_data['mobile']
            emergency_contract = form.cleaned_data['emergency_contract']
            student_object_new = models.Student.objects.create(customer_id=customer_id,qq=qq,mobile=mobile,
                                          emergency_contract=emergency_contract)
            student_object_new.class_list.add(class_list.id)
        else:
            student_object.class_list.add(class_list.id)

    label_name = [get_choice_text('费用类型','pay_type'),'paid_fee','class_list',get_date_text('申请日期','apply_date'),
                  get_choice_text('状态','confirm_status')]

