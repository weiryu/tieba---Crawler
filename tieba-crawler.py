# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 12:58:45 2018

@author: weir
"""

import urllib
import urllib.request
import re

#
class Tool:
    #去除Img标签
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行标签替换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD = re.compile('<td>')
    #将段落开头换为\n加两个空格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #剔除其余标记
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x=re.sub(self.removeImg,"",x)
        x=re.sub(self.removeAddr,"",x)
        x=re.sub(self.replaceLine,"\n",x)
        x=re.sub(self.replaceTD,"\t",x)
        x=re.sub(self.replacePara,"\n  ",x)
        x=re.sub(self.replaceBR,"\n",x)
        x=re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()
        
#百度贴吧爬虫类        
class BDTB:
    #初始化，传入基地址，是否只看楼主参数
    def __init__(self,baseUrl,seeLZ,floorTag):
        #base连接地址
        self.baseURL=baseUrl
        #是否只看楼主
        self.seeLZ = '?see_lz='+str(seeLZ)
        #HTML标签剔除工具类对象
        self.tool=Tool()
        #全局file变量，文件写入操作对象
        self.file=None
        #楼层编号，初始为1
        self.floor=1
        #默认标题，在没有成功获取标题时使用
        self.dafaultTitle=u"百度贴吧"
        #是否写入楼分隔符的标志
        self.floorTag = floorTag
        #浏览器头信息初始化
        self.user_agent='Mozilla/4.0(compatible;MSIE 5.5;Windows NT)'
        self.headers={'User-Agent':self.user_agent}
        
    #传入页码，获取该页帖子的代码
    def getPage(self,pageNum):
        try:
            #构建url
            url=self.baseURL+self.seeLZ+'&pn='+str(pageNum)
            print("url")
            print("------")
            print(url)
            print("------")
            request=urllib.request.Request(url,headers=self.headers)
            response=urllib.request.urlopen(request)
            content= response.read().decode('utf-8',errors="ignore")
            # response.close()
            return content
        #无效连接，报错
        except urllib.request.URLError as e:
            if hasattr(e,"reason"):
                print(u"连接失败",e.reason)  
                return None
                
    #获取帖子标题
    def getTitle(self,page):
        page = self.getPage(1)
        pattern = re.compile(r'<h3 class="core_title_txt pull-left text-overflow.*?>(.*?)</h3>',re.S)
        result = re.search(pattern,page)
        if result:
            #存在则返回标题
            print("贴子标题：")
            print(result.group(1))
            return result.group(1).strip()
        else:
            return None
            
    #获得作者
    def getPageAuthor(self,page):
        page = self.getPage(1)
        pattern=re.compile(r'<div class="louzhubiaoshi beMember_fl j_louzhubiaoshi" author="(.*?)">',re.S) 
        author=re.search(pattern,page)
        if author:
            print("作者：")
            print(author.group(1).strip())
            return author.group(1).strip()
        else:
            return None
            
    #获取帖子页数和评论数
    def getPageNum(self,page):
        page = self.getPage(1)
        pattern = re.compile(r'<li class="l_reply_num".*? style="margin-right:3px">(.*?)</span>.*?<span class="red">(.*?)</span>',re.S)
        result = re.search(pattern,page)
        if result:
            #存在则返回页数和评论数
            print("回复数%s，评论数%s\n" %(result.group(1).strip(),result.group(2).strip()))
            return result.group(2).strip()
        else:
            return None
        
      
    def getContent(self,page):
        #匹配所有楼层内容
        pattern = re.compile(r'<div id="post_content_.*?>(.*?)</div>',re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            #文本去标签化，在前后加入换行符
            content ="\n"+self.tool.replace(item)+"\n"
            contents.append(content)
        return contents
    
    def setFileTitle(self,title):
        if title is not None:
            #标题不为None，成功获取标题
            self.file = open(str(1)+'.txt','a+',encoding='utf-8')
        else:
            self.file = open(self.dafaultTitle+'.txt','a+',encoding='utf-8')
            
    def writeData(self,contents):
        #向文件写入每一楼信息
        for item in contents:
            if self.floorTag=='1':
                #楼之间的分隔符
                floorLine='\n'+str(self.floor)+u"------------------------------"
                self.file.write(floorLine)
            self.file.write(str(item))
            self.floor+=1

    
    def start(self):
        indexPage = self.getPage(1)
        print("indexPage")
        print(indexPage)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        self.getPageAuthor(indexPage)
        if pageNum == None:
            print("URL失效")
            return
        try:
            print("该帖子共有"+str(pageNum)+'页')
            for i in range(1,int(pageNum)+1):
                print("正在写入第"+str(i)+"页")
                page = self.getPage(i)
                ## print(page)
                contents= self.getContent(page)
                print(contents)
                self.writeData(contents)
        #写入异常
        except IOError as e:
            print("写入异常"+e.message)
        finally:
            print("写入任务完成")
        self.file.close()
            
            
print("请输入帖子代号\n")
baseURL = 'http://tieba.baidu.com/p/'+str(input(u'http://tieba.baidu.com/p/'))
seeLZ =input("只获取楼主发言输入1，否则输入0\n")
floorTag=input("写入楼层信息输入1，否则输入0\n")
bdtb = BDTB(baseURL,seeLZ,floorTag)
bdtb.start()