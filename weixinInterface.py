﻿# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json
from lxml import etree

class WeixinInterface:

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="liangfei" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr

    def POST(self):     
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        msgType=xml.find("MsgType").text
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        if msgType=='text':
            content=xml.find("Content").text#获得用户所输入的内容
            #翻译
            if content[0:2] == u"翻译":
                post = content[2:]
                text = post.encode('utf-8')
                tx = urllib2.quote(text)
                baseurl=r'http://fanyi.youdao.com/openapi.do?keyfrom=zhilutianshi&key=293831118&type=data&doctype=json&version=1.1&q='
                url = baseurl+tx
                r=urllib2.urlopen(url)
                fy=json.loads(r.read())
                trans=fy['translation']
                return self.render.reply_text(fromUser,toUser,int(time.time()),' '.join(trans))
            if content[0:2] == u"天气":
                a=content[2:]
                if len(a):
                    a=a.encode('GB2312')
                    baseurl = [('http://php.weather.sina.com.cn/xml.php?city=%s&password=DJOYnieT8234jlsK&day={}' % text).format(str(i)) for i in range(0,3)]
                else:
                    baseurl = ['http://php.weather.sina.com.cn/xml.php?city=%B1%B1%BE%A9&password=DJOYnieT8234jlsK&day={}'.format(str(i)) for i in range(0,3)]
                city=[]
                for url in baseurl:
                    tq_xml = urllib2.urlopen(url).read()
                    xml = etree.fromstring(tq_xml)
                    cy = xml.find("status1").text
                    city.append(cy)
                return self.render.reply_text(fromUser,toUser,int(time.time()),' '.json(city))
            else:
                return self.render.reply_text(fromUser,toUser,int(time.time()),u"我现在还在开发中，还没有什么功能，您刚才说的是："+content)
        elif msgType =='image':
            pass
        else:
            pass