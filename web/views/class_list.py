from django.utils.safestring import mark_safe
from django.urls import reverse
from web import models
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler,get_date_text,get_mtom_text,StarkModelForm
from .base import PermissionHandle


class ClassListModelForm(StarkModelForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'
        widgets = {
            'start_date':DateTimePickerInput
        }

class ClassListHandler(PermissionHandle,StarkHandler):

    def display_course(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return '班级'
        return '%s %s 期'%(obj.course,obj.period)

    def display_course_record(self,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return '上课记录'
        name = reverse('stark:web_courserecord_list', kwargs={'class_id': obj.pk})
        return mark_safe('<a href="%s">上课记录</a>'%name)

    label_name = ['school','manage_teacher',get_mtom_text('任课教师','teach_teacher'),
                  get_date_text('开班日期','start_date'),display_course,display_course_record]
    model_form_class = ClassListModelForm


