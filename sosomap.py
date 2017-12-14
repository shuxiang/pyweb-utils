#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:soso地图api
作者:shuxiang29
mail:shuxiang29@gmail.com
设计流程:
'''
__revision__ = "1.0.0.20120727"
__appname__  = "sosomap"
__author__   = "shuxiang29"
__email__    = "shuxiang29@gmail.com"
__modules__  = "requests"

import sys
import time
import os.path
import traceback
import string
import requests
import json
from baidumap import bd_decrypt
from zmisc import unicode2utf8

apikey = '5KEBZ-JTFHF-DEUJR-J63GY-E3VKE-GDBUI' #shuxiang29 qq 申请 开房利器

def format_cmp(str1,str2):
    """
        格式化之后比较字符串
        @param str1: 字符串1
        @param str2: 字符串2
        @param : 返回比较结果
    """
    nstr1 = str1
    nstr1 = nstr1.replace('（','(')
    nstr1 = nstr1.replace('）',')')

    nstr2 = str2.replace('（','(')
    nstr2 = nstr2.replace('）',')')

    print nstr1, nstr2
    if  nstr1 == nstr2:
        return True
    try:
        if nstr1.endswith(nstr2.split('(')[1].split(')')[0]):
            return True
    except:
        pass
    return False

def Geocoding(address , city):
    """
        通过qq接口，根据地址和城市获取坐标
        @param address: 地址
        @param city: 城市
        @return results: 包含状态、经纬度以及精度的字典，如下
                {
                "status":"OK",
                "result":{
                    "location":{
                        "lng":114.324675,
                        "lat":30.652687
                    },
                    "precise":1
                }
                }
    """
    url = "http://api.map.qq.com/?c=%s&l=11&wd=%s&pn=0&rn=40&qt=poi&output=jsonp&fr=mapapi&cb=cbh4koz4f4&t=%s" % (city, address, int(time.time()))

    results = {}
    try:
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
            "Content-Type": "text/plain; charset=UTF-8",
            "Referer":"http://api.map.soso.com/doc/tooles/picker.html",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"
        }

        data = requests.get(url, headers = headers, timeout=2)
        if data.status_code <> 200:
            return results
        text = data.text
    except:
        traceback.print_exc()
        return results

    #print "return:",text

    jtext = text.split('(',1)[1].rsplit(')',1)[0]
    result = json.loads(jtext)
    error = result['info']['error']
    if error <> 0:
        return results

    results['city'] = {}
    detail = result['detail']
    if 'city' in detail:
        city = detail['city']
        cityname =  city['cname'].encode('utf8')
        clnt = city['pointx']
        clat = city['pointy']

        results['city'] = {'name':cityname,'lat':clat,'lnt':clnt}

    results['pois'] = []
    rpois = results['pois']

    if not detail.has_key('pois'):
        return results
    pois = detail['pois']
    #print type(pois),len(pois)
    for poi in pois:
        pname = poi['name'].encode('utf8')
        nlnt = poi['pointx']
        nlat = poi['pointy']
        ntel = poi['phone'].encode('utf8')
        addr = poi['addr'].encode('utf8')
        rpois.append((pname,nlat,nlnt,{'tel':ntel,'addr':addr}))

    return results

def printResults(results):
    """
        格式化输出
        @param results: 打印内容
    """
    if results.has_key('city'):
        for k in results['city']:
            print k,'=',results['city'][k]

    print "-" * 20
    for result in results['pois']:
        pname,lat, lnt, exts = result
        print pname, lat, lnt
        for k in exts.keys():
            print "\t",k,'=', exts[k]

def getPois(address):
    """
        获取打点区域
        @param address: 地址信息
        @return lat,lon: 返回经纬度
    """
    city = ''
    start = time.time()
    try:
        results = Geocoding(address, city)

        if 'pois' in results and len(results['pois']) > 0:
            pname,lat, lnt, exts = results['pois'][0]
            return str(lat), str(lnt)
    except:
        print "getPois Exception [%s]" % address
        traceback.print_exc()

    usedtime = time.time() - start
    print "getPois address[%s] usedtime:%f" % (address, usedtime)

    return '',''


def get_mapimage(gcenter, bcenter, pois, zoom='13', w=300, h=300):
    """
        通过百度和搜搜map接口，根据中心位置信息获取百度静态地图地址
        @param gcenter: 谷歌地标中心位置
        @param bcenter: 百度地标中心位置
        @param pois: 标记区域
        @param zoom: 缩放比例
        @param w: 图片宽度
        @param h: 图片高度
        @return url: 返回静态图地址
    """
    lat, lnt = gcenter

    print lat, lnt
    url_base = 'http://api.map.baidu.com/staticimage?width=%d&height=%d&markers={markers}&zoom={zoom}&markerStyles={markerStyles}' %(w,h)
    url_base = 'http://st.map.soso.com/api?size=%d*%d&center={center}&zoom={zoom}&markers={markers}' %(w,h)
    #http://st.map.soso.com/api?size=604*300&center=116.31993,40.03304&zoom=13&markers=116.31993,40.03304,1|116.31634,40.02369,2
    center = "%s,%s" % (lnt, lat)
    markers='%s,%s,red,0|' % (lnt, lat)
    i = 1
    for poi in pois:
        lat, lnt = poi
        markers += "%s,%s,blue,%d|" % (lnt,lat,i)
        i += 1

    url = url_base.replace('{center}', center)
    url = url.replace('{center}', center)
    url = url.replace('{markers}', markers)
    url = url.replace('{zoom}', zoom)

    return url

def getAddress(lat, lnt):
    """
    逆地址解析：根据坐标获取地址,传入坐标为百度坐标

    地址解析：根据地址获取坐标
    http://api.map.baidu.com/geocoder?address=地址&output=输出格式类型&key=用户密钥&city=城市名

    逆地址解析：根据坐标获取地址
    http://api.map.baidu.com/geocoder?location=纬度,经度&output=输出格式类型&key=用户密钥

    备注：

    1. city属于可选参数，通常情况可以不使用，若解析无结果，请尝试增加此字段。
    2. 支持名胜古迹、标志性建筑物名称解析返回百度经纬度坐标，如address=“百度大厦”。
    3. 支持使用“*路与*路交叉口”方式解析返回百度经纬度坐标，若地址库中存在该地址描述，返回百度经纬度坐标。
    4. 若解析status字段为OK，若结果内容为空，原因分析及可尝试方法：

    地址库里无此数据，本次结果为空。
    加入city字段重新解析；
    将过于详细或简单的地址更改至省市区县街道重新解析；
    5. 特别提醒：逆地址解析location参数传入的参数格式是(纬度lat，经度lng)。

    {
        "status":"OK",
        "result":{
            "location":{
                "lng":116.380752,
                "lat":39.887269
            },
            "formatted_address":"北京市西城区菜市口南大街58号",
            "business":"菜市口,陶然亭,白纸坊",
            "addressComponent":{
                "city":"北京市",
                "district":"西城区",
                "province":"北京市",
                "street":"菜市口南大街",
                "street_number":"58号"
            },
            "cityCode":131
        }
    }

    """
    url = "http://apis.map.qq.com/ws/geocoder/v1?location=%s,%s&coord_type=3&output=json&key=%s" % (str(lat), str(lnt), apikey)

    results = {}
    try:
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
            "Content-Type": "text/plain; charset=UTF-8",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"
        }

        data = requests.get(url, headers = headers, timeout=0.3)
        if data.status_code <> 200:
            return results
        text = data.text
    except:
        traceback.print_exc()
        return results

    print "return:",text

    result = unicode2utf8(json.loads(text))
    error = result['status']
    if error <> 'OK':
        return results

    return result

def getAddressGoogle(glat, glnt):
    '''
    逆地址解析：根据坐标获取地址,传入坐标为谷歌坐标系（火星坐标系)
    '''

    lat, lnt = bd_decrypt(float(glat), float(glnt))
    return getAddress(lat, lnt)


if __name__ == "__main__":

    if len(sys.argv) <= 1:
        address, city = '百步亭花园温馨苑', '武汉'
        results = Geocoding(address, city)
        print address, city
        print "-" * 40
        printResults(results)


        address, city = '如家快捷酒店 徐东友谊大道店', '武汉'
        results = Geocoding(address, city)
        print address, city
        print "-" * 40
        printResults(results)


    if len(sys.argv) > 1:

        print getPois(sys.argv[1])
        if 0:
            city = sys.argv[1]
            city = ''
            address = sys.argv[2]
            results = Geocoding(address, city)
            print address, city
            print "-" * 40
            printResults(results)



