# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 18:14:53 2016

@author: weir
"""

import urllib.request
import re

def open_url(url):
    req=urllib.request.Request(url)
    page=urllib.request.urlopen(req)
    html=page.read().decode('UTF-8')
    return html
    
def get_img(html):
    p=r'<img class="BDE_Image" src="([^"]+\.jpg)"'
    imglist=re.findall(p,html)
    n=0
    for each in imglist:
        n+=1
        filename='照片'+str(n)+'.jpg'
        local=r'D:\pi'
        urllib.request.urlretrieve(each,local+"\\"+filename)
        
if __name__=='__main__':
	#示例网址
    url='http://tieba.baidu.com/p/4392472369'
    get_img(open_url(url))