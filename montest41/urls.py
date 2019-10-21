"""montest4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from login.views import login, logout,index
# from devmanage.views import ip_view, add_ip, add_dev, search_dev, search_ip, mod_dev, mod_ip, dev_view
from devmanage.views import ip_view, add_ip, search_ip,asktime,deltime
from service.views import service_show,getshow

admin.autodiscover()
# from django.conf.urls import handler404, handler500

# handler404 = "webserver.views.page_not_found"
# handler500 = "webserver.views.page_error"


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'login/', login),
    url(r'logout/',logout),
    # url(r'accounts/login', index.as_view()),
    url(r'dev_manage/', service_show),
    url(r'^getshow',getshow,name='getshow'),
    url(r'ip_manage/', ip_view),
    url(r'add_ip/', add_ip),
    # url(r'add_dev/$', add_dev),
    url(r'search_ip/$',search_ip),
    # url(r'search_dev/$',search_dev),
    # url(r'mod_ip/$', mod_ip),
    # url(r'mod_dev/$', mod_dev),
    url(r'^asktime',asktime,name='asktime'),
    url(r'^deltime',deltime,name='deltime'),
    url(r'', index),
    # url(r'ip_manage/ajax', ajax),


]