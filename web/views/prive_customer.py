from django.urls import reverse
from django.utils.safestring import mark_safe
from stark.service.v1 import StarkHandler,StarkModelForm,get_choice_text,get_mtom_text
from .base import PermissionHandle

from web import models
class PrivateCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant']


class PrivateCustomerHandler(PermissionHandle,StarkHandler):

    def save(self,request,form,is_update,*args,**kwargs):
        if not is_update:
            current_user_id = request.session['user']['id']
            form.instance.consultant_id = current_user_id
        form.save()

    def multi_private(self,request):
        current_user_id = request.session['user']['id']
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list,consultant_id=current_user_id).update(consultant_id=None)

    multi_private.text = '从私户移除'

    def queryset_obj(self,request,*args,**kwargs):
        current_user_id = request.session['user']['id']
        return self.model_class.objects.filter(consultant_id=current_user_id)


    def display_record(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return '跟进详情'
        reverse_record = reverse('stark:web_record_list',kwargs={'customer_id':obj.pk})
        return mark_safe("<a href='%s'>跟进记录</a>"%reverse_record)

    def payment_record(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return '缴费记录'
        reverse_record = reverse('stark:web_paymentrecord_list',kwargs={'customer_id':obj.pk})
        return mark_safe("<a href='%s'>缴费</a>"%reverse_record)

    label_name = [StarkHandler.display_checkbox,'name','qq',get_mtom_text('咨询课程','course'),
                  get_choice_text('状态','status'),display_record,payment_record]

    action_list = [multi_private]
    model_form_class = PrivateCustomerModelForm

