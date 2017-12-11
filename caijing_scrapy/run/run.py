# -*- coding: utf-8 -*-
import os
import threading
from threading import Timer
import subprocess
import signal
import sys

#开启线程操作
class SpiderThread(threading.Thread):
    #重写构造函数,可以添加参数以便传递给线程主体调用
    def __init__(self,args):
        super(SpiderThread,self).__init__()      #调用父类构造函数
        self.args = args
    def run(self):
        scrapyrun(self.args)


scrapy = {}     #爬虫池
thread = []     #线程池
def scrapyrun(sig):
    global scrapy
    scrapy[sig] = subprocess.Popen('python3 spidersun.py '+sig,shell=True)      #不添加shell 会报not fond错误 在linux中
    # scrapy['returnCode'] = subprocess.Popen('python spidersun.py '+sig,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) #将输出传递出来 不会自动显示
    print(sig,scrapy[sig],'开始运行')
for arg in sys.argv[1:]:        #sys.argv[0] 位当前脚本名
    #注册一个线程
    thread.append(SpiderThread(arg))
    #开启线程
    thread[-1].start()
while True:
    mn = input('Runing:')
    if('stop' in mn):
        try:
            spider = mn.split(',')[1]
            scrapy[spider].send_signal(signal.CTRL_C_EVENT)      #发送Ctrl+c 命令
            scrapy[spider].kill()
            print('kelld:',spider)
        except Exception as e:
            print(e)
            print('input agrent....')
