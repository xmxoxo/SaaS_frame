#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import argparse
from svrlib import *
#from sanic.response import text
from sanic import Sanic, response
from sanic_jinja2 import SanicJinja2 as SanicJinja

# -----------------------------------------
# 版本号 
version = '0.2.0' 
# 任务清单
task_list = []

def main():
    #　创建应用
    app = Sanic(__name__)
    app.static('/static', './static')
    tp = SanicJinja(app)

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
                #strCmd = "python ./app/run.py %s %s"% (app_config, tid)
            else:
                strCmd = "python ./app/run.py %s %s"% (app_config,tid)
            app['command_line'] = strCmd

            task_list.append(app)

            # 启动
            runtask2(app)
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
    main()
