import json
from random import randrange
from django.shortcuts import render_to_response
from django.http import HttpResponse
# from devmanage.views import APIView
from django.http import JsonResponse
from pyecharts.charts import Bar
from pyecharts import options as opts
from devmanage.models import Datas,Ip
import time,datetime

# Create your views here.
def service_show(request):  ## 展示         第一次访问返回一个数据
    
    name_status = Ip.objects.filter(status="ON")
    # return render_to_response( 'dev_manage.html',{'username':request.user.username},lst)
    return render_to_response('dev_manage.html',{ 'name_status':name_status})

def getshow(request):  ## 展示         第一次访问返回一个数据
    memory_list = {'Length': [], 'Datetime': []}
    if request.is_ajax:
        if request.method == 'POST':
            basen = request.POST.get("name")  # 获取其中的某个键的值
            print(basen)

            starttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())#开始查询时间
            time1 = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
            endtime=time1-datetime.timedelta(hours=1) #查询时间的结束
            nottime =time1-datetime.timedelta(weeks=1)
            #删除超过7天的数据
            seven_data =Datas.objects.filter(utime__lte=nottime)
            print(seven_data)
            if seven_data:
                seven_data.delete()
            # endtime =  time.strftime("%Y-%m-%d %H:%M", time.localtime()-(starttime.tm_hour))
            print(starttime, endtime)
            name = []
            jq = []
            # i = datetime.datetime.now()
            # print(i)
# 		# 过滤在某时间段的数据
#             test3 = Datas.objects.filter(basename=basen).filter(utime__lte=starttime,utime__gte=endtime)
#             print (list(test3))
            for i in Datas.objects.filter(basename=basen).filter(utime__lte=starttime,utime__gte=endtime):
                # memory_list['Datetime'].append(datetime.strftime(i.utime, "%Y-%m-%d %H:%M:%S"))
                # memory_list['Length']=i.lendata
                time2=i.utime
                name.append(time2.strftime(" %H:%M:%S"))
                # print(i.utime)
                jq.append(i.lendata)

            # 构造一个字典
            ret = {'name': name, 'jq': jq}
            # print(ret)
            #dumps() 将字典转变为json形式，
            easyList =json.dumps(ret)
            return JsonResponse(ret)
            # return JsonResponse('dev_manage.html', {'name_status': name_status})

#             return render(req, 'login.html', {'uf': uf, 'nowtime': nowtime, 'password_is_wrong': True})



