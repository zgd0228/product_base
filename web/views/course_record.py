from django.conf.urls import url
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory
from django.shortcuts import HttpResponse,render
from stark.service.v1 import StarkHandler,StarkModelForm,get_date_text
from web import models
from .base import PermissionHandle

class CourseRecordModelForm(StarkModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ['day_num','teacher']

class StudyRecordModelForm(StarkModelForm):
    class Meta:
        model = models.StudyRecord
        fields = ['record']

class CourseRecordHandler(PermissionHandle,StarkHandler):

    model_form_class = CourseRecordModelForm

    def display_attendance(self,obj,is_header=None,*args,**kwargs):
        if is_header:
            return '考勤'
        name = "%s:%s"%(self.site.namespace,self.get_url_name('attendance'))
        attendance_url = reverse(name,kwargs={'study_id':obj.pk})

        return mark_safe('<a href="%s">考勤</a>'%attendance_url)

    def attendance_list(self,request,study_id,*args,**kwargs):

        study_object_list = models.StudyRecord.objects.filter(course_record_id=study_id).all()
        for item in study_object_list:
            print(item.course_record.class_object.student_set.all())
        study_formset = modelformset_factory(models.StudyRecord,form=StudyRecordModelForm,extra=0)
        formset = study_formset(queryset=study_object_list)
        if request.method == "POST":
            formset = study_formset(queryset=study_object_list,data=request.POST)
            if formset.is_valid():
                formset.save()
                return render(request,'study_record.html',locals())
        return render(request,'study_record.html',locals())

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<class_id>\d+)/$', self.wrapper(self.list), name=self.get_list_url_name),
            url(r'^add/(?P<class_id>\d+)/$', self.wrapper(self.add),name=self.get_add_url_name),
            url(r'change/(?P<class_id>\d+)/(?P<id>\d+)/$',self.wrapper(self.change),name=self.get_change_url_name),
            url(r'delete/(?P<class_id>\d+)/(?P<id>\d+)/$',self.wrapper(self.delete),name=self.get_delete_url_name),
            url(r'attendance/(?P<study_id>\d+)/$',self.wrapper(self.attendance_list),name=self.get_url_name('attendance')),
        ]
        patterns.extend(self.extra_urls())
        return patterns


    def queryset_obj(self,request,*args,**kwargs):
        class_id = kwargs.get('class_id')
        return self.model_class.objects.filter(class_object_id=class_id)

    def display_change(self, obj=None, is_header=None, *args, **kwargs):

        '''
        编辑按钮的url或者表头的编辑
        :param obj:
        :param is_header:
        :return:
        '''

        if is_header:
            return '编辑'
        name = self.reverse_change_url(class_id = kwargs['class_id'],id=obj.pk)

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
        name = self.reverse_delete_url(class_id = kwargs['class_id'],id=obj.pk)
        return mark_safe("<a href='%s'>删除</a>" %name )

    def save(self,request,form,is_update,*args,**kwargs):
        class_id = kwargs.get('class_id')
        if not is_update:
            form.instance.class_object_id = class_id
        form.save()

    def action_multi_course_init(self, request , *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        class_id = kwargs.get('class_id')

        class_object = models.ClassList.objects.filter(id=class_id).first()
        if not class_object:
            return HttpResponse('班级不存在')
        student_obj_list = class_object.student_set.all()

        for course_id in pk_list:
            course_obj = models.CourseRecord.objects.filter(id=course_id,class_object_id=class_object.id).first()
            if not course_obj:
                continue
            study_record_exists = models.StudyRecord.objects.filter(course_record = course_obj).exists()
            if study_record_exists:
                continue
            study_record_obj_list = [models.StudyRecord(student_id=stu.id,course_record_id=course_id)
                                     for stu in student_obj_list]

            models.StudyRecord.objects.bulk_create(study_record_obj_list,batch_size=100)


    action_multi_course_init.text = '批量初始化考勤'

    action_list = [action_multi_course_init]

    label_name = [StarkHandler.display_checkbox,'class_object','day_num','teacher',
                  get_date_text('上课时间','date'),display_attendance]




