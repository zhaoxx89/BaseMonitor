from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
# Create your views here.
from .models import Users

def index(request):
    '''判断用户是否登陆'''
    if not  request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    else:
        username=request.user.username
        return render_to_response('ip_manage.html',{'username':username})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password :
            user = auth.authenticate(username=username,password=password)
            if user is not None and user.is_active:
                auth.login(request,user)
            #request.session['username']=username
            # return HttpResponseRedirect('/index/',context_instance=RequestContext(request))
                return HttpResponseRedirect('/index/')
            else:
                 return render_to_response('login.html',{'login_error':'用户名或密码错误!'})
        else:
            return render_to_response('login.html', {'login_error': '用户名或密码不能为空!'})
    else:
        return render_to_response('login.html')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')