#!/usr/local/python3/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'zhiyi'
import time,threading

#假定这是你的银行存款
balance = 0
lock = threading.Lock()

def change_it(n):
    #先存后去，结果应该为0
    global balance
    balance = balance + n
    balance = balance - n
    #print('%s thread %s'%(balance,threading.current_thread().name))

def run_thread(n):
    for i in range(1000000):
        #先要获取锁：
        lock.acquire()
        try:
            change_it(n)
        finally:
            #改完一定要释放锁
            lock.release()

t1 = threading.Thread(target=run_thread,args=(5,))
t2 = threading.Thread(target=run_thread,args=(8,))
t1.start()
t2.start()
t1.join()
t2.join()
print(balance)