#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import os
import sys
#import psutil
from time import sleep
from tqdm import tqdm
import requests

# ����pid��֪ͨ�����
def save_pid(tid, pid_file=''):
    import os
    import requests
    try:
        if tid:
            pid = os.getpid()
            print('pid:%s'%pid)
            # �ѽ���ID���浽�ļ�
            if pid_file:
                with open(pid_file, 'a') as f:  
                    f.write(str(pid))
            # ֪ͨϵͳ
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

# ֪ͨ�����
print(n, tid)
save_pid(tid)


# ģ�ⳤʱ������
#for i in tqdm(range(1000*n), ncols=60):
total = 1000*n
for i in range(total):
	sleep(0.01)
    if i % 100==0:
        print('taskid:%s, process: %.2f%%' % (tid, i/total))
   

if __name__ == '__main__':
    pass

