from stark.service.v1 import site
from web import models
from web.views.user import UserInfoHandler
from web.views.school import SchoolHandler
from web.views.depart import DepartHandler
from web.views.course import CourseHandler
from web.views.class_list import ClassListHandler
from web.views.prive_customer import PrivateCustomerHandler
from web.views.pub_customer import PublishCustomerHandler
from web.views.record import RecordHandler
from web.views.payment import PaymentHandler
from web.views.payment_approval import PaymentApprovalHandler
from web.views.student import StudentHandler
from web.views.score_record import ScoreRecordHandler
from web.views.course_record import CourseRecordHandler


site.register(models.School,SchoolHandler)
site.register(models.Depart,DepartHandler)
site.register(models.UserInfo,UserInfoHandler)
site.register(models.Course,CourseHandler)
site.register(models.ClassList,ClassListHandler)
site.register(models.Customer,PublishCustomerHandler,'pub')
site.register(models.Customer,PrivateCustomerHandler,'priv')
site.register(models.Record,RecordHandler)
site.register(models.PaymentRecord,PaymentHandler)
site.register(models.PaymentRecord,PaymentApprovalHandler,'conf')
site.register(models.Student,StudentHandler)
site.register(models.ScoreRecord,ScoreRecordHandler)
site.register(models.CourseRecord,CourseRecordHandler)