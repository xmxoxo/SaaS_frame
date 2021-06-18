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

# import asyncio
from threading import Thread

# -----------------------------------------

# 进程类
class ProcessInfo():
    def __init__(self, pid=0):
        self.pid = pid
        self.memory = 0
        self.info = ''
        self.tid = 0
        self.app_name = ''
        self.app_config = ''
        self.app_cmdline = ''
        self.process_name = ''
        self.cmdline = ''       # 命令行
        self.create_time = 0    # 启动时间
        self.num_threads = 0    # 进程数量
        self.alive = False      # 是否运行
        self.update_time = 0    # 更新时间
        self.update()

    def update(self, pid=0):
        if pid:
            self.pid = pid
        pids = psutil.pids()
        if self.pid in pids and self.pid!=0:
            self.alive = True
            process = psutil.Process(self.pid)
            # process.connections() 网络连接
            self.process_name = process.name()
            self.create_time = process.create_time()
            self.num_threads = process.num_threads()
            self.cmdline = ' '.join(process.cmdline())

            self.memory = process.memory_info().rss
            #self.info = 'Used Memory: %.3f MB' % (self.memory / 1024 / 1024 )
            self.info = '{:,.2f}MB'.format(self.memory / 1024 / 1024 )
        else:
            self.pid = 0
            self.alive = False
            self.memory = 0
            self.info = '0MB'
            self.process_name = ''
            self.create_time = 0
            self.num_threads = 0
            self.cmdline = ''

        self.update_time = time.time()

    def __str__(self):
        self.update()    
        ret = 'pid=%s, process_name=%s, alive=%s, update_time=%s info=%s cmdline=%s' % (
                self.pid, self.process_name, self.alive, self.update_time, self.info, self.cmdline)
        return ret
        
    def stop(self):
        try:
            os.kill(self.pid, psutil.signal.SIGILL)
            self.update()
            return 1
        except :
            return 0

    def restart(self):
        pass
        #os.system(self.cmdline)
        
    def status(self):
        self.update()
        if self.alive:
            return 'running'
        else:
            return 'end'
        
        # return self.alive
# -----------------------------------------

class ProcessList():
    def __init__(self, pids=[]):
        self.pids = pids
        self.memory = 0
        self.process = {}
        self.update()
    
    def update(self, pids=[]):
        if pids:
            self.pids = pids
        memory = 0
        for pid in self.pids:
            self.process[pid] = ProcessInfo(pid=pid)
            memory += self.process[pid].memory
        
        self.memory = memory

    def append(self, app):
        pro = ProcessInfo()
        pro.tid = app['tid']
        pro.app_name = app['app_name']
        pro.app_config = app['app_config']
        pro.app_cmdline = app['command_line']
        
        self.process[tid] = pro

    def setpid(self, tid, pid):
        pass

        

# -----------------------------------------
# 版本号 
version = '0.2.0' 

task_list = []

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

# 定义了一个装饰器 asyncz 用于创建线程 
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
            strCmd = app.get('command_line','')
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
    try:
        url = 'http://127.0.0.1:8000/push'
        cname = 'task_dat'
        cont = json.dumps(content)
        dat = {'cname': cname, 'content':cont}
        r = requests.get(url, params=dat, timeout=3)
        # print('post dat:%s' % r.text)
    except Exception:
        pass
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
            strCmd = "start cmd /c python ./app/run.py %s %s"% (app_config, tid)
        else:
            strCmd = "python run.py %s %s"% (n,tid)
        app['command_line'] = strCmd

        task_list.append(app)

        # 启动
        runtask(app)
    return response.json({"return": 1})

# 接收端
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

# icomet 服务端推送
# app.add_task(notify_server_started())
app.run("0.0.0.0", 9100, workers=1)

if __name__ == '__main__':
    pass

