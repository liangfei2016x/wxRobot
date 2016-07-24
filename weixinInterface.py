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
                a=(content[2:]).strip()
                if len(a):
                    a.encode('utf-8')
                    one_music=anymusic(a)
                    musiclist=[one_music]
                else:
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
            elif content[0:2] == u"快递":
                a =str(content[2:]).strip()
                if len(a):
                    kd=kd100(a)
                else:
                    kd=kd100()
                return self.render.reply_text(fromUser,toUser,int(time.time()),kd)
            else:
                res=tuling(content)
                rep_content=res['text']
                return self.render.reply_text(fromUser,toUser,int(time.time()),rep_content)
        elif msgType =='image':
            pass
        else:
            pass
#图灵
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
#点歌
def anymusic(s_name):
    s_url = r'http://apis.baidu.com/geekery/music/query?s=%s&size=5&page=1' % s_name
    key = '3b45811f4b67acba8e670d04ff93b08d'
    headers = {'apikey':key}
    r=requests.get(s_url,headers=headers)
    response=json.loads(r.text)
    hash_text=response['data']['data'][2]['hash']
    url = r'http://apis.baidu.com/geekery/music/playinfo?hash=%s' % hash_text
    res=requests.get(url,headers=headers)
    resp=json.loads(res.text)
    url_name=resp['data']['url']
    fileName=resp['data']['fileName']
    fileDes=u'好听你就点个赞吧'
    song_list=[url_name,fileName,fileDes]
    return song_list
#快递
def kd100():
    numb='881443775034378914'
    numb_url=r'http://www.kuaidi100.com/autonumber/autoComNum?text=%s' % numb
    r=requests.post(numb_url)
    response=json.loads(r.text)
    kd_name=response['auto'][0]['comCode']
    q_url=r'http://www.kuaidi100.com/query?type={0}&postid={1}'.format(kd_name,numb)
    q_data=requests.get(q_url)
    data=json.loads(q_data.text)
    msg_data=data['data']
    string=u""
    for msg in msg_data:
        string=string+msg['time']+' '+msg['context']+'\n'
    return string