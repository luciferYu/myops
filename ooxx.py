import urllib.request
import re
import os
from bs4 import BeautifulSoup
import time

def url_open(url):
    #req = urllib.request.Request(url)
    #req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0')
    #response = urllib.request.urlopen(url)

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  
    req = urllib.request.Request(url=url, headers=headers)  
    response = urllib.request.urlopen(req) 
    
    html = response.read()
    return html

def get_page(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    #regex = re.compile(r'"current-comment-page">\[(\d*)\]')
    #ccp = regex.search(html)
    data = BeautifulSoup(html)
    ccp = data.find('span',{'class':'current-comment-page'}).get_text()
    return str(ccp[1:4])

def get_jpg_address(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    data = BeautifulSoup(html,"html.parser")
    ccp = data.find_all('a',href=re.compile('jpg'))
    #regex = re.compile(r'"//(.*?\.jpg)"')
    #ccp = regex.findall(html)
    l1 = []
    for link in ccp:
        piclink = link.get('href')
        l1.append(piclink)
    return l1

def save_imgs(folder,img_addrs):
    for eachpic in img_addrs:
            try:
                filename = eachpic.split('/')[-1]
                picaddr = 'http:' + eachpic
                print(picaddr)
                with open(filename,'wb') as f:
                    img = url_open(picaddr)
                    f.write(img)
                    time.sleep(0.5)
            except:
                continue

    
def download_mm(folder='mm',page=10):
    if not os.path.exists('.\mm'):
        os.mkdir(folder)
    os.chdir(folder)
    url = 'http://jandan.net/ooxx'
    pagenum = get_page(url)
    #print(pagenum)
    for i in range(int(pagenum) - page , int(pagenum)):
        mmurl = 'http://jandan.net/ooxx/page-' + str(i) + '#comments'
        #print(mmurl)
        address = get_jpg_address(mmurl)
        #print(address)
        save_imgs(folder,address)
            
        


download_mm(page = 50)
        




