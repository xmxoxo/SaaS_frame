#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import os
import sys
#import psutil
from time import sleep
from tqdm import tqdm
import requests

# 保存pid并通知服务端
def save_pid(tid, pid_file=''):
    import os
    import requests
    try:
        if tid:
            pid = os.getpid()
            print('pid:%s'%pid)
            # 把进程ID保存到文件
            if pid_file:
                with open(pid_file, 'a') as f:  
                    f.write(str(pid))
            # 通知系统
            url = 'http://127.0.0.1:9100/pid'
            dat = {'tid': tid, 'pid':pid}
            r = requests.post(url, data=dat, timeout=3)
            print('post dat:%s' % r.text)
    except :
        pass

n = 1
if len(sys.argv)>=2:
    n = int(sys.argv[1])

tid = ''
if len(sys.argv)>=3:
    tid = sys.argv[2]

# 通知服务端
print(n, tid)
save_pid(tid)


# 模拟长时间任务
#for i in tqdm(range(1000*n), ncols=60):
total = 1000*n
for i in range(total):
	sleep(0.01)
    if i % 100==0:
        print('taskid:%s, process: %.2f%%' % (tid, i/total))
   

if __name__ == '__main__':
    pass

