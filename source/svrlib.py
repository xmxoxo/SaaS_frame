#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import os
import json
import sys
import requests
import time
import psutil
# import asyncio
from threading import Thread
from multiprocessing import Process
import subprocess


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


def UpdateAlive(task_list):
    ''' 更新任务状态列表
    '''
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

def async_process(f):
    def wrapper(*args, **kwargs):
        #p = Thread(target=f, args=args, kwargs=kwargs)
        p = Process(target=f, args=(args,))
		#p = subprocess.Popen(strCmd, shell=True)
        
        p.start()
    
    return wrapper

def runtask(app):
    ''' 启动进程
    '''
    @asyncz
    #@async_process
    def dowork_t(app):
        try:
            strCmd = app.get('command_line','')
            if strCmd:
                #os.system(strCmd)
                subprocess.run(strCmd, shell=True)
        except :
            return 0
    
    dowork_t(app)

def dowork(strCmd):
    if strCmd:
        os.system(strCmd)
        #subprocess.run(strCmd, shell=True)

def runtask1(app):
    try:
        strCmd = app.get('command_line','')
        p = Thread(target=dowork, args=(strCmd,))
        p.start()
    except :
        return 0

def runtask2(app):
    try:
        strCmd = app.get('command_line','')
        p = Process(target=dowork, args=(strCmd,), daemon=False)
        p.start()
    except Exception as e :
        print(e)
        return 0

def icomet_send(content): #url, cname, 
    ''' 使用icomet通知消息
    '''
    try:
        url = 'http://127.0.0.1:8000/push'
        cname = 'task_dat'
        cont = json.dumps(content)
        dat = {'cname': cname, 'content':cont}
        r = requests.get(url, params=dat, timeout=3)
        # print('post dat:%s' % r.text)
    except Exception:
        pass


if __name__ == '__main__':
    pass

