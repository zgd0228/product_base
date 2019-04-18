from django.conf.urls import url
from stark.service.v1 import StarkHandler,get_choice_text,get_date_text
from .base import PermissionHandle


class PaymentApprovalHandler(PermissionHandle,StarkHandler):

    def multi_change(self,request):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            payment_obj = self.model_class.objects.filter(id=pk,confirm_status=1).first()
            if not payment_obj:
                continue
            payment_obj.confirm_status = 2
            payment_obj.save()

            payment_obj.customer.status = 1
            payment_obj.customer.save()

            payment_obj.customer.student.student_status = 2
            payment_obj.customer.student.save()
    multi_change.text = '批量确认'

    def multi_reject(self,request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list,confirm_status=1).update(confirm_status=3)
    multi_reject.text = '批量驳回'

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.list), name=self.get_list_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_label_name(self,request,*args,**kwargs):
        '''
        为以后的扩展预留，根据不同的情况显示不同的内容（列）
        :return:
        '''
        value = []
        if self.label_name:
            value.extend(self.label_name)
        return value

    action_list = [multi_change,multi_reject]
    has_add_btn = False
    order_list = ['confirm_status']
    label_name = [StarkHandler.display_checkbox,'customer',get_choice_text('费用类型','pay_type'),'paid_fee','class_list',get_date_text('申请日期','apply_date'),
                  get_choice_text('确认状态','confirm_status'),'consultant']


