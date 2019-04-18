from stark.service.v1 import StarkHandler
from .base import PermissionHandle


class CourseHandler(PermissionHandle,StarkHandler):
    label_name = ['title']