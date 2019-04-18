from django.shortcuts import redirect,render,HttpResponse,Http404
from django.http import JsonResponse
from django.conf.urls import url
from web import models
from web.utils.md5 import hash_md5
from rbac.service.permission_session import *


def login(request):
    '''
    用户登录
    :param request:
    :return:
    '''
    response = {'user':None,'msg':None}
    if request.is_ajax():
        user = request.POST.get('user')
        pwd = hash_md5(request.POST.get('pwd'))
        user_obj = models.UserInfo.objects.filter(name=user,pwd=pwd).first()
        if not user_obj:
            response['msg'] = '用户名或密码错误'
        else:
            response['user'] = user
            request.session['user'] = {'id':user_obj.id,'name':user_obj.name}
            init_session(request,user_obj)
        return JsonResponse(response)
    return render(request,'login.html')

def logout(request):
    '''
    注销
    :param request:
    :return:
    '''
    request.session.delete()
    return redirect('/login/')
def index(request):

    return render(request,'index.html')