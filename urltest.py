#!/usr/local/python3/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'zhiyi'
from urllib import request
from pprint import pprint
import random
import asyncio


def testtmsapi():
    try:
        targeturl = 'http://testtmsapi.fruitday.com'
        req = request.Request(targeturl)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        proxies = ['123.13.204.109:9999','58.23.16.240:80','124.88.67.82:80','124.88.67.82:81']
        proxy = random.choice(proxies)
        #print(proxy)
        proxy_support = request.ProxyHandler({'http':proxy})
        opener =  request.build_opener(proxy_support)
        #print('open')
        request.install_opener(opener)
        response =  request.urlopen(targeturl)
        #print('res')
        html = response.read().decode('utf-8')
        return html
    except:
        print('error')
        pass




for i in range(100):
    #print(i)
    print(testtmsapi())