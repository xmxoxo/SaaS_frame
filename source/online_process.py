#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import os
import sys
from sanic import Sanic, response
#import asyncio
from threading import Thread
import time
from multiprocessing import Process


taskid = []

# 判断PID是否存活 Is PID alive
def IsAlive(pid):
    if pid == 0:
        return False
    else:
        pids = psutil.pids()
        return pid in pids


#定义了一个装饰器 asyncz 用于创建线程 
def asyncz(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def async_process(f):
    def wrapper(*args, **kwargs):
        p = Process(target=f, args=args, kwargs=kwargs)
        p.start()
        pid = p.pid
        print('子进程的pid是%s' % pid)
    return wrapper

app = Sanic('async demo')


def dowork(n):
    try:
        # 组织命令行，然后启动程序  start
        strCmd = "start cmd /c python run.py %s"%n
        os.system(strCmd) 
    except :
        pass
        return 0

def run_process(n):
    p = Process(target=dowork, args=(n,))
    p.start()
    pid = p.pid
    print('子进程的pid是%s' % pid)

def run(n):

    #@async_process
    @asyncz
    def dowork(n):
        try:
            # 组织命令行，然后启动程序  start
            strCmd = "start cmd /c python run.py %s"%n
            os.system(strCmd) 
        except :
            pass
            return 0
    
    dowork(n)


@app.route("/")
async def index(request):
    global taskid
    return response.json({"return": taskid})

@app.route("/task")
async def task(request):
    n = request.args.get('n')
    if n:
        # run(n)
        run_process(n)
    return response.json({"return": 1})

@app.route("/pid")
async def cpid(request):
    pass
    tid = request.args.get('tid')
    pid = request.args.get('pid')
    return response.json({"return": 1})


app.run("0.0.0.0", 9100, workers=1)

if __name__ == '__main__':
    pass

