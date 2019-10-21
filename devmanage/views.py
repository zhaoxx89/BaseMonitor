# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import RequestContext
from devmanage.models import Ip,Datas,Monitor
from django.db.models import Q
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
# from service.views import *
import threading
import datetime
import sys
import socket,socketserver
import collections
import time ,json
import json
import requests
# from wxpy import *
# from wechat_sender import *
# from wechat_sender import Sender

each_page=10  #每页表格列数


# Create your views here.
exitFlag = 0     # 线程提出标志
BUF_SIZE = 2048  # 设置缓冲区大小
socket_dict ={}  # 创建空字典
monitor_dict ={} #创建报警空字典
threadList =[]  # 创建线程列表
threads = []    # 创建空闲列表
lock =threading.Lock()
global client_error
client_error=1
# freeList
obj = collections.deque(["t1","t2","t3","t4","t5","t6","t7","t8","t9","t9","t10","t11","t12","t13","t14","t15"])
# 填充队列

def asktime(request):
    # response = HttpResponse()
    global client_error
    if request.is_ajax():
        # 直接获取所有的post请求数据
        data = request.POST
        # 获取其中的某个键的值
        name = request.POST.get("name")
        print(data)
        # test2 = Ip()#实例化数据库
        test2 = Ip.objects.get(basename= name)

        #判断字典的长度
        #获取字典的长度
        if (len(socket_dict)<15):
            # 创建启动需要的线程名
            t=obj.popleft()
            print(t)
            #在线程字典中添加相应字典元素
            # socket_dict[name] = t
            # 开启线程

            # t.start()
            # lock.acquire()
            try:

                t = MyThread(name, test2.ipaddr, test2.ports, test2.ostype)
                t.start()
                # time.sleep(0.01)
                time.sleep(1)
                print(client_error)
                if (client_error == 0): #启动正常
                    # print(client_error)
                    socket_dict.update({name: t})
                    threads.append(t)
                    # print(test2.ports)
                    test2.status = 'ON'
                    test2.save()
            except Exception as e:
                client_error =4  #超时
                print(e)
        # # 将前端传来的数据再次传回前端，只是为了测试
        response = JsonResponse({"name": name,"biao": client_error})
        # response = JsonResponse(json.dumps({"name": name}))
        return response


@login_required
def ip_view(request):
    '''show ip list'''
    #del ip
    if request.method == 'POST' and request.POST:
        ip = request.POST.getlist('post_ip')
        for i in ip:
            # p=Ip.objects.get(ipaddr=i)
            p = Ip.objects.get(basename=i)
            p.delete()

    # ip_list=Ip.objects.all().order_by('ipaddr')
    ip_list = Ip.objects.all().order_by('basename')
    paginator=Paginator(ip_list,each_page)
    page=request.GET.get('page',1)

    try:
        show_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        show_list = paginator.page(1)
    except (EmptyPage,InvalidPage):
        # If page is out of range (e.g. 9999), deliver last page of results.
        show_list = paginator.page(paginator.num_pages)
    return render_to_response('ip_manage.html',{'username':request.user.username,'show_list':show_list,'paginator':paginator})



def deltime(request):
    # response = HttpResponse()
    if request.is_ajax():
        # 直接获取所有的post请求数据
        data = request.POST
        # 获取其中的某个键的值
        name = request.POST.get("name")
        print(data)
        print(name)
        test1 = Ip.objects.get(basename= name)
        test1.status = 'OFF'
        test1.save()
        # if (len(threads)>0 and (name in socket_dict)):
        if (name in socket_dict):
            # list.remove(obj)
            ddel=socket_dict[name]
            #判断子线程是否活跃
            if(ddel.isAlive()):
            #防止阻塞
                ddel.join(1.5)
            print (ddel)
            threads.remove(ddel)
            del socket_dict[name];  # 删除键是name的条目
            # threads.remove(ddel)
            obj.append(ddel)
        # 将前端传来的数据再次传回前端，只是为了测试
        response = JsonResponse({"name": name})
        return response

@login_required
def add_ip(request):
    '''add ip'''
    if request.method == 'POST':
        # ip=request.POST.get('ipaddr')
        ip = request.POST.get('basename')
        pport=request.POST.get('ports')
        if len(Ip.objects.filter(basename=ip)) != 0:
            return render_to_response('add_ip.html',{'username':request.user.username,'add_error':'基站名已经存在!'})
        elif len(Ip.objects.filter(ports=pport)) != 0:
            return render_to_response('add_ip.html', {'username': request.user.username, 'add_error': '端口已经存在!'})
        else:
            p=Ip(
                basename=request.POST.get('basename'),
                ipaddr=request.POST.get('ipaddr'),
                ports=request.POST.get('ports'),
                ostype=request.POST.get('ostype'),
                rate=request.POST.get('rate'),
                status=request.POST.get('status')
                )
            p.save()
            return render_to_response('ip_manage.html', {'username': request.user.username})
    else:
        return render_to_response('add_ip.html',{'username':request.user.username})


@login_required
def search_ip(request):
    '''search ip list'''
    if 'search' in request.GET and request.GET.get('search'):
        s_text=request.GET.get('search')
        if len(s_text) != 0:
            qset=(
                Q(basename__icontains = s_text)|
                Q(ipaddr__icontains = s_text)|
                Q(ports__icontains = s_text)|
                Q(ostype__icontains = s_text)|
                Q(rate__icontains=s_text)

                )
            ip_list=Ip.objects.filter(qset).order_by('basename')
            if len(ip_list) == 0:
                return render_to_response('ip_manage.html',{'username':request.user.username,'search_error':'查找内容不存在！'})

        paginator=Paginator(ip_list,each_page)
        page=request.GET.get('page',1)
        try:
            show_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_list = paginator.page(1)
        except (EmptyPage,InvalidPage):
            # If page is out of range, deliver last page of results.
            show_list = paginator.page(paginator.num_pages)
        return render_to_response('ip_manage.html',{'username':request.user.username,'show_list':show_list,'paginator':paginator,'s_text':s_text})

# @login_required
# def search_dev(request):
#     '''search dev list'''
#     if 'search' in request.GET and request.GET.get('search'):
#         s_text=request.GET.get('search')
#         if len(s_text) != 0:
#             qset=(
#                 Q(ipaddr__icontains = s_text)|
#                 Q(cpu__icontains = s_text)|
#                 Q(memory__icontains = s_text)|
#                 Q(location__icontains = s_text)|
#                 Q(product__icontains = s_text)|
#                 Q(platform__icontains = s_text)|
#                 Q(sn__icontains = s_text)
#                 )
#             ip_list=Device.objects.filter(qset).order_by('ipaddr')
#             if len(ip_list) == 0:
#                 return render_to_response('dev_manage.html',{'username':request.user.username,'search_error':'查找内容不存在！'})
#
#         paginator=Paginator(ip_list,each_page)
#         page=request.GET.get('page',1)
#         try:
#             show_list = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             show_list = paginator.page(1)
#         except (EmptyPage,InvalidPage):
#             # If page is out of range, deliver last page of results.
#             show_list = paginator.page(paginator.num_pages)
#         return render_to_response('dev_manage.html',{'username':request.user.username,'show_list':show_list,'paginator':paginator,'s_text':s_text})

class MyThread(threading.Thread):
    def __init__(self, name, ip, port, type):
        threading.Thread.__init__(self)
        self.name = name
        self.ip = ip
        self.port = port
        self.type = type

    def run(self):
        # 加锁
        # lock.acquire()
        typetcp = self.type
        if typetcp == "client":
            clienthread(self.name, self.ip, self.port)
        elif typetcp == "server":
            serverthread(self.name, self.ip, self.port)
        # elif typetcp == "NtripClient":
        #     ntripclient(self.name, self.ip, self.port)

def clienthread(baseName, addr, port):
    global client_error
    lip = addr
    lport = int(port)
    Name = baseName
    # # 连接服务器
    # hostPort = (lip, lport)

    # 创建套接字socket
    try:
        # 连接服务器
        hostPort = (lip, lport)
        tcpclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpclient.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
        tcpclient.connect(hostPort)  # 链接套接字
        client_error = 0
        # print(client_error)
    except socket.gaierror as e:
        client_error = 2  # 标志socket ip有异常
        tcpclient.close()
    except socket.error as e:
        client_error = 1  # 表示
        tcpclient.close()
    else:
        time.sleep(1.5)
        while baseName in socket_dict:
            # queueLock.acquire()
            # i =0
            # 接收数据
            data = tcpclient.recv(BUF_SIZE)
            nowtime = datetime.datetime.now()
            # nt = newtime.strftime('%Y-%m-%d %H:%M:%S')
            strnow =  nowtime.strftime( '%Y-%m-%d %H:%M:%S')
            p1 = Datas(
                basename = Name,
                lendata = len(data),
                utime = strnow
                )
            p1.save()#保存数据
            # p1 = Datas(basename=Name, databytes=recv_data, udate=strnow)
            # p1.save()
            # 判断数据是否断开或字节少
            if (len(data)>100):
                i=0
            else:
                i += 1
                print(Name, '的链接断开了！')  # 等待接收但接收为空则客户端断开
                # errdata =Monitor(
                #     basename_e =Name,
                #     data_byte =len(data),
                #     p_time =strnow
                # )
                # errdata.save()#保存数据
                #
                #   # 启动正常
                #     # print(client_error)
                monitor_dict.update({Name: i})
                print(monitor_dict)
                if ( i % 10 ==0)and (i<361):
                    msg = Name+str(i)+"秒断开连接"

                    wechat = WeChat(corpid, secret, agentid)
                    wechat.send_message(msg)

            # time.sleep(1)
            # p1.save()  # 保存数据
            # continue
        tcpclient.shutdown(socket.SHUT_RDWR)
        tcpclient.close()
    return client_error  # 没有作用


def serverthread(baseName, addr, port):
    global client_error
    # Ip = addr
    Ip = socket.gethostbyname(socket.gethostname())
    Port = int(port)
    Name = baseName
    # 连接服务器
    HostPort = (Ip, Port)
    # self.addr = (self.ip, self.port)
    try:
        tcpserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置地址复用
        tcpserver.bind(HostPort)  # 绑定地址端口
        tcpserver.listen(1)
        client_error = 0
    except socket.error  as msg:
        client_error = 3  # 表示端口有异常
        sys.exit()
        tcpserver.close()
    else:
        # conn, c_add = tcpserver.accept()  # 链接套接字
        client, client_addr = tcpserver.accept()  # 接收TCP连接, 并返回新的套接字和地址, 阻塞函数
        print('Connected by', client_addr)
        time.sleep(2)
        while baseName in socket_dict:
            # while True:
            i=0
            data = client.recv(BUF_SIZE)  # 从客户端接收数据
            newtime = datetime.datetime.now()
            nt = newtime.strftime('%Y-%m-%d %H:%M:%S')
            p2 = Datas(
                basename=Name,
                lendata=len(data),
                utime=nt
            )  # 实例化数据库
            p2.save()  # 保存数据
            if (len(data)>100):
                i=0
            else:
                i += 1
            # # 判断客户端是否断开
            # if not data:
            #     print(Name, nt + '的链接断开了！')  # 等待接收但接收为空则客户端断开
            #     errdata2 = Monitor(
            #         basename_e=Name,
            #         data_byte=len(data),
            #         p_time=nt
            #     )
            #     errdata2.save()  # 保存数据
                # 报警机制
                monitor_dict.update({Name: i})
                print(monitor_dict)
                if (i % 10 == 0) and (i < 361):
                    msg = Name + i + "秒断开连接"

                    wechat = WeChat(corpid, secret, agentid)
                    wechat.send_message(msg)

            # else:
            #     print(data, nt)
            # client.sendall(data)  # 发送数据到客户端
            # time.sleep(1)
            # continue
        tcpserver.shutdown(socket.SHUT_RDWR)
        tcpserver.close()
    return client_error  # 没有作用
        # # 要判断无数据30分钟无数据进入，休眠时间变为60

    # def  ntripclient(self):
    #     pass
    #
    # def stop(self):
    #     self.__stop = True
    #     exitFlag = 1     # 线程提出标志


agentid = 1000002
secret = 'gXD3oruxCnWh7qSMqZ315YDMOpXiYRvCIYP15BrmvTo'
corpid = 'ww67181be5ecef09a2'


##通过文件助手给登录的微信号发消息
# bot.file_helper.send('port 80 nice!')

class WeChat(object):
    def __init__(self, corpid, secret, agentid):
        self.url = "https://qyapi.weixin.qq.com"
        self.corpid = corpid
        self.secret = secret
        self.agentid = agentid

    # 获取企业微信的 access_token
    def access_token(self):
        url_arg = '/cgi-bin/gettoken?corpid={id}&corpsecret={crt}'.format(
            id=self.corpid, crt=self.secret)
        url = self.url + url_arg
        response = requests.get(url=url)
        text = response.text
        self.token = json.loads(text)['access_token']

    # 构建消息格式
    def messages(self, msg):
        values = {
            "touser": '@all',
            "msgtype": 'text',
            "agentid": self.agentid,
            "text": {'content': msg},
            "safe": 0
        }
        # python 3
        # self.msg = (bytes(json.dumps(values), 'utf-8'))
        # python 2
        self.msg = json.dumps(values)

    # 发送信息
    def send_message(self, msg):
        self.access_token()
        self.messages(msg)

        send_url = '{url}/cgi-bin/message/send?access_token={token}'.format(
            url=self.url, token=self.token)
        response = requests.post(url=send_url, data=self.msg)
        errcode = json.loads(response.text)['errcode']

        if errcode == 0:
            print('Succesfully')
        else:
            print('Failed')


# msg = "mysql 出现错误"
#
# # wechat = WeChat(corpid, secret, agentid)
# # wechat.send_message(msg)