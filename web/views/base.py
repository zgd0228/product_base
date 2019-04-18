from django.conf import settings


class PermissionHandle(object):
    # 是否显示添加按钮
    def get_add_btn(self, request, *args, **kwargs):
        # 当前用户所有的权限信息
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        if self.get_add_url_name not in permission_dict:
            return None
        return super().get_add_btn(request, *args, **kwargs)

    # 是否显示编辑和删除按钮
    def get_label_name(self, request, *args, **kwargs):

        # 当前用户所有的权限信息
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        print(permission_dict)
        value = []
        if self.label_name:
            value.extend(self.label_name)
            if self.get_change_url_name in permission_dict and self.get_delete_url_name in permission_dict:
                value.append(type(self).display_edit_del)
            elif self.get_change_url_name in permission_dict:
                value.append(type(self).display_change)
            elif self.get_delete_url_name in permission_dict:
                value.append(type(self).display_delete)
        return value