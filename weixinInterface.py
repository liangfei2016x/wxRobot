# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json
import random
import requests
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
                post = (content[2:]).strip()
                text = post.encode('utf-8')
                tx = urllib2.quote(text)
                baseurl=r'http://fanyi.youdao.com/openapi.do?keyfrom=zhilutianshi&key=293831118&type=data&doctype=json&version=1.1&q='
                url = baseurl+tx
                r=urllib2.urlopen(url)
                fy=json.loads(r.read())
                trans=fy['translation']
                return self.render.reply_text(fromUser,toUser,int(time.time()),' '.join(trans))
            #天气
            elif content[0:2] == u"天气":
                a=(content[2:]).strip()
                if len(a):
                    a=a.encode('GB2312')
                    baseurl = [('http://php.weather.sina.com.cn/xml.php?city=%s&password=DJOYnieT8234jlsK&day={}' % a).format(str(i)) for i in range(0,3)]
                else:
                    baseurl = ['http://php.weather.sina.com.cn/xml.php?city=%B1%B1%BE%A9&password=DJOYnieT8234jlsK&day={}'.format(str(i)) for i in range(0,3)]#默认为北京
                weather=[]
                for url in baseurl:
                    tq_xml = urllib2.urlopen(url).read()
                    xml = etree.fromstring(tq_xml)
                    dt = xml.xpath('//Profiles/Weather/savedate_weather')[0].text
                    st = xml.xpath('//Profiles/Weather/status1')[0].text
                    tm1 = xml.xpath('//Profiles/Weather/temperature1')[0].text
                    tm2 = xml.xpath('//Profiles/Weather/temperature2')[0].text
                    data = dt+" "+st+" "+tm2+u"°C"+"-"+tm1+u"°C"+"\n"
                    weather.append(data)
                return self.render.reply_text(fromUser,toUser,int(time.time()),','.join(weather))
            #点歌
            elif content[0:2] == u"点歌":
                musiclist=[
                            [r'http://m2.music.126.net/K1SFXCvWf8BO9VEpSvx2ew==/7967061257205150.mp3','Jam',u'七月上(妞!快来听)'],
                            [r'http://m2.music.126.net/D7GY-8m9japXRmzBPlfovA==/3445869444824734.mp3',u'金玟岐',u'小幸运(妞!快来听)'],
                            [r'http://m2.music.126.net/hDrQ4OGIV1C25vw3H03MLA==/1213860837073174.mp3',u'梁静茹',u'小手拉大手(妞!快来听)'],
                            [r'http://m2.music.126.net/F8K_9OAgMUuc8qrFeFDPrg==/3308430488137023.mp3',u'回音哥',u'海绵宝宝(妞!快来听)'],
                            ]
                music = random.choice(musiclist)
                musicURL = music[0]
                musicDes = music[1]
                musicTitle = music[2]
                return self.render.reply_music(fromUser,toUser,int(time.time()),musicTitle,musicDes,musicURL)
            else:
                res=tuling(content)
                rep_content=res['text']
                return self.render.reply_text(fromUser,toUser,int(time.time()),u"我现在还在开发中，还没有什么功能，您刚才说的是："+rep_content)
        elif msgType =='image':
            pass
        else:
            pass

def tuling(msg):
    url = r'http://www.tuling123.com/openapi/api'
    APIKEY = '5f27804952aaf87cad2da3ba134114be'
    data = {
            'key':APIKEY,
            'info':msg.encode('utf-8'),
    }
    r=requests.post(url,data=data)
    response = json.loads(r.text)
    return response
