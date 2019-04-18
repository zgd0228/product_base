from stark.service.v1 import StarkHandler
from .base import PermissionHandle
class DepartHandler(PermissionHandle,StarkHandler):
    label_name = ['title']