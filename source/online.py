#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import os
import json
import sys
import requests
import time
import psutil
from sanic import Sanic, response
#from sanic.response import text
from sanic_jinja2 import SanicJinja2 as sj

#import asyncio
from threading import Thread


version = '0.1.0'

task_list = []

# 判断PID是否存活 Is PID alive
def IsAlive(pid):
    if pid == 0:
        return False
    else:
        pids = psutil.pids()
        return pid in pids

def UpdateAlive(task_list):
    if not task_list:
        return []
    else:
        all_pids = psutil.pids()
        #print('all_pids:', all_pids)
        for i, item in enumerate(task_list):
            pid = item.get('pid',0)
            if pid==0: continue
            #print('pid:', pid)
            if int(pid) in all_pids:
                task_list[i]['status'] = 'running'
            else:
                task_list[i]['status'] = 'end'
                #task_list.pop(i)
    return task_list

#定义了一个装饰器 asyncz 用于创建线程 
def asyncz(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def runtask(app):
 
    @asyncz
    def dowork(app):
        try:
            n = app.get('app_config')
            tid = app.get('tid')
            strCmd = app.get('cmd','')
            # tid = int(time.time()*1000)
            # 组织命令行，然后启动程序  start
            # strCmd = "start cmd /c python run.py %s %s"% (n,tid)
            if strCmd:
                os.system(strCmd) 
        except :
            pass
            return 0
    
    dowork(app)

def icomet_send(content): #url, cname, 
    url = 'http://127.0.0.1:8000/push'
    cname = 'task_dat'
    cont = json.dumps(content)
    dat = {'cname': cname, 'content':cont}
    r = requests.get(url, params=dat, timeout=3)
    # print('post dat:%s' % r.text)


#-----------------------------------------

app = Sanic(__name__)
app.static('/static', './static')
tp = sj(app)


async def notify_server_started():
    @asyncz
    def notiy():
        while 1:
            time.sleep(1)
            global task_list
            if task_list:
                task_list = UpdateAlive(task_list)
                icomet_send(task_list)
    notiy()


@app.route("/")
@tp.template('index.html')  
async def index(request):
    #global task_list
    #task_list = UpdateAlive(task_list)
    #return {'task_list': task_list, 'version': version}
    return {'version': version}


@app.route("/status")
async def status(request):
    global task_list
    task_list = UpdateAlive(task_list)
    return response.json({"return": task_list})

@app.route("/task", methods=['POST'])
async def task(request):
    app = request.json
    # n = request.args.get('n')
    if app:
        print('app:', app)
        # 组织数据，记录到任务表
        app_config = app.get('app_config')
        app_name = app.get('app_name')
        tid = int(time.time()*1000)
        app['tid'] = tid
        # 组织命令行
        if os.name == 'nt':
            strCmd = "start cmd /c python run.py %s %s"% (app_config,tid)
        else:
            strCmd = "python run.py %s %s"% (n,tid)
        app['cmd'] = strCmd

        task_list.append(app)

        # 启动
        runtask(app)
    return response.json({"return": 1})

# 接收端口
@app.route("/pid", methods=['POST'])
async def cpid(request):
    pass
    tid = request.form.get('tid')
    pid = request.form.get('pid')
    if tid and pid:
        # 查找
        for task in task_list:
            if str(task.get('tid'))==str(tid): 
                #task_list.append({'tid':tid, 'pid':pid})
                task['pid'] = pid

    return response.json({"return": 1})


app.add_task(notify_server_started())
app.run("0.0.0.0", 9100, workers=1)

if __name__ == '__main__':
    pass

