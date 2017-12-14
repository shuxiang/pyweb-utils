#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:baidu地图api v2版本
设计流程:
'''
__revision__ = "2.0.0.20140717"
__appname__  = "baidumap"
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
import base64
from zmisc import unicode2utf8

if 0:
    import httplib
    httplib.HTTPConnection.debuglevel = 0


apikey = 'GKgBNwWbGNMY8zSfhItuzCkx'

http = requests.Session()

http.headers.update({'Accept-Encoding':'gzip,deflate,sdch', 'Connection':'keep-alive'})

def Geocoding(address , city):
    """
    返回值
    {
        status: 0,
        result: {
            location: {
                lng: 116.30814954222,
                lat: 40.056885091681
            },
            precise: 1,
            confidence: 80,
            level: "商务大厦"
        }
    }

    """
    url = "http://api.map.baidu.com/geocoder/v2/?city=%s&address=%s&output=json&ak=%s" % (city, address, apikey)

    results = {}
    try:
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
            "Content-Type": "text/plain; charset=UTF-8",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"
        }
        
        data = http.get(url, headers = headers, timeout=1.0)
        if data.status_code <> 200:
            return results
        text = data.text
    except:
        traceback.print_exc()
        return results

    print "return:",text   

    result = json.loads(text)
    error = result['status']
    if error <> 0:
        return results

    results['pois'] = []
    rpois = results['pois']

    if len(result['result']) < 1:
        return results
    poi = result['result']['location']
    lat = poi['lat']
    lnt = poi['lng']
    precise = result['result']['precise']
    rpois.append(('',lat,lnt, {'precise':precise}))

    return results

def getAddress(lat, lnt):
    """
    逆地址解析：根据坐标获取地址,传入坐标为百度坐标

    地址解析：根据地址获取坐标
    http://api.map.baidu.com/geocoder/v2/?address=地址&output=输出格式类型&ak=用户密钥&city=城市名

    逆地址解析：根据坐标获取地址
    http://api.map.baidu.com/geocoder/v2/?location=纬度,经度&output=输出格式类型&ak=用户密钥

    备注：

    1. city属于可选参数，通常情况可以不使用，若解析无结果，请尝试增加此字段。
    2. 支持名胜古迹、标志性建筑物名称解析返回百度经纬度坐标，如address=“百度大厦”。
    3. 支持使用“*路与*路交叉口”方式解析返回百度经纬度坐标，若地址库中存在该地址描述，返回百度经纬度坐标。
    4. 若解析status字段为0，若结果内容为空，原因分析及可尝试方法：

    地址库里无此数据，本次结果为空。
    加入city字段重新解析；
    将过于详细或简单的地址更改至省市区县街道重新解析；
    5. 特别提醒：逆地址解析location参数传入的参数格式是(纬度lat，经度lng)。

    {
	"status": 0,
	"result": {
		"location": {
			"lng": 116.38719979829,
			"lat": 39.893459434921
		},
		"formatted_address": "北京市西城区潘家胡同21号",
		"business": "菜市口,虎坊桥,陶然亭",
		"addressComponent": {
			"city": "北京市",
			"district": "西城区",
			"province": "北京市",
			"street": "潘家胡同",
			"street_number": "21号"
		},
		"cityCode": 131
	}
    }

    """
    url = "http://api.map.baidu.com/geocoder/v2/?location=%s,%s&output=json&ak=%s" % (str(lat), str(lnt), apikey)

    results = {}
    try:
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
            "Content-Type": "text/plain; charset=UTF-8",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"
        }

        data = requests.get(url, headers = headers, timeout=1.0)
        if data.status_code <> 200:
            return results
        text = data.text
    except:
        traceback.print_exc()
        return results

    print "return:",text

    result = unicode2utf8(json.loads(text))
    error = result['status']
    if error <> 0:
        return results

    result['status']='OK'
    return result

def getAddressGoogle(glat, glnt):
    '''
    逆地址解析：根据坐标获取地址,传入坐标为谷歌坐标系（火星坐标系)
    '''

    lat, lnt = bd_encrypt(float(glat), float(glnt))
    return getAddress(lat, lnt)


def Place(address , city):

    url = "http://api.map.baidu.com/place/v2/search?&region=%s&query=%s&output=json&ak=%s&page_size=20" % (city, address, apikey)

    results = {}
    try:
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
            "Content-Type": "text/plain; charset=UTF-8",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"
        }
        
        data = requests.get(url, headers = headers, timeout=5)
        if data.status_code <> 200:
            return results
        text = data.text
    except:
        traceback.print_exc()
        return results

    print "return:",text   

    result = json.loads(text)
    error = result['status']
    if error <> 0:
        return results

    results['pois'] = []
    rpois = results['pois']

    if len(result['results']) < 1:
        return results
    for r in result['results']:
        pname = r['name'].encode('utf8')
        addr = r.get('address',u'').encode('utf8')
        tel = r.get('telephone',u'').encode('utf8')
        poi = r['location']
        nlat = poi['lat']
        nlnt = poi['lng']
        rpois.append((pname,nlat,nlnt,{'tel':tel,'addr':addr}))

    return results


def printResults(results):

    if results.has_key('city'):
        for k in results['city']:
            print k,'=',results['city'][k]

    print "-" * 20
    for result in results.get('pois',[]):
        pname,lat, lnt, exts = result
        print pname, lat, lnt
        for k in exts.keys():
            print "\t",k,'=', exts[k]


def convert(lat,lnt):

    url = "http://api.map.baidu.com/geoconv/v1/?from=3&to=5&coords=%s,%s&ak=%s" % (lnt, lat, apikey)
    data = requests.get(url, timeout=5)
    if data.status_code <> 200:
        return '1',0,0

    print url, data.text
    result = json.loads(data.text)
    error = result['status']
    x = str(result['result'][0]['x'])
    y = str(result['result'][0]['y'])
    return error, y, x

def get_mapimage(gcenter, bcenter, pois, zoom='13', w=300, h=300):

    if len(bcenter) != 2:
        lat, lnt = gcenter
        flag, blat, blnt = convert(lat, lnt)
        if flag != 0:
            return ''
    else:
        blat, blnt = bcenter

    print blat, blnt
    url_base = 'http://api.map.baidu.com/staticimage?width=%d&height=%d&markers={markers}&zoom={zoom}&markerStyles={markerStyles}' %(w,h)

    center = "%s,%s|" % (blnt, blat)
    markers=center
    markerStyles='m,0,0x00FFFF|'
    i = 1
    for poi in pois:
        lat, lnt = poi
        markers += "%s,%s|" % (lnt,lat)
        markerStyles += "l,%d,0xFF3900|" % i
        i += 1

    url = url_base.replace('{center}', center)
    url = url.replace('{markers}', markers)
    url = url.replace('{markerStyles}', markerStyles)
    url = url.replace('{zoom}', zoom)

    return url

from  math import sqrt, sin, atan2, cos

def bd_encrypt(gg_lat, gg_lon):
    '''
    const double x_pi = 3.14159265358979324 * 3000.0 / 180.0;

    void bd_encrypt(double gg_lat, double gg_lon, double &bd_lat, double &bd_lon)
    {
        double x = gg_lon, y = gg_lat;
        double z = sqrt(x * x + y * y) + 0.00002 * sin(y * x_pi);
        double theta = atan2(y, x) + 0.000003 * cos(x * x_pi);
        bd_lon = z * cos(theta) + 0.0065;
        bd_lat = z * sin(theta) + 0.006;
    }
    '''

    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    x = gg_lon
    y = gg_lat
    z = sqrt(x * x + y * y) + 0.00002 * sin(y * x_pi)
    theta = atan2(y, x) + 0.000003 * cos(x * x_pi)
    bd_lon = z * cos(theta) + 0.0065
    bd_lat = z * sin(theta) + 0.006

    return bd_lat, bd_lon

def bd_decrypt(bd_lat, bd_lon):
    '''
    void bd_decrypt(double bd_lat, double bd_lon, double &gg_lat, double &gg_lon)
    {
        double x = bd_lon - 0.0065, y = bd_lat - 0.006;
        double z = sqrt(x * x + y * y) - 0.00002 * sin(y * x_pi);
        double theta = atan2(y, x) - 0.000003 * cos(x * x_pi);
        gg_lon = z * cos(theta);
        gg_lat = z * sin(theta);
    }
    '''

    x_pi = 3.14159265358979324 * 3000.0 / 180.0

    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = sqrt(x * x + y * y) - 0.00002 * sin(y * x_pi)
    theta = atan2(y, x) - 0.000003 * cos(x * x_pi)
    gg_lon = z * cos(theta)
    gg_lat = z * sin(theta)

    return gg_lat, gg_lon


if __name__ == "__main__":

    usage = """Usage:
      baidumap.py geocoding
      baidumap.py geocoding2
      baidumap.py place 
      baidumap.py convert 
      baidumap.py convert2 
      baidumap.py convert3 
      baidumap.py convert4 
      baidumap.py getmapimage 

    """
    from docopt import docopt
    args = docopt(usage)
    print "args:",args

    if args.get('geocoding', False):

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

    if args.get('place', False):
        address, city = '如家快捷酒店', '武汉'
        results = Place(address, city)
        print address, city
        print "-" * 40
        printResults(results)


    if args.get('convert', False):
        print convert('30.597597','114.350909')

    if args.get('getmapimage', False):

        print get_mapimage(('30.597597','114.350909'),(),(('30.595597','114.350009'),('30.599597','114.352909'),('30.599597','114.350009')))


    if args.get('convert2', False):
        lat, lnt = 30.597597,114.350909
        flag, blat, blnt = convert(str(lat), str(lnt))

        glat, glnt = bd_decrypt(float(blat), float(blnt))
        print "glat=%f, glat=%s delta=%f" % (lat, glat, lat - float(glat))
        print "glnt=%s, glnt=%s delta=%f" % (lnt, glnt, lnt - float(glnt))


    if args.get('convert3', False):
        blnt, blat = 116.34885675438, 40.045321458289
        glnt2, glat2 = 116.342253581, 40.0396733485
        glnt, glat = 116.341609955, 40.040546369

        oklat, oklnt = 40.039733189748446,116.34238243119626

        lat, lnt= bd_decrypt(blat, blnt)
        print "oklat=%f, glat=%f delta=%f" % (oklat, lat, lat - oklat)
        print "oklnt=%s, glnt=%s delta=%f" % (oklnt, lnt, lnt - oklnt)

    if args.get('convert4', False):
        print convert('39.887269','116.380752')
        print bd_encrypt(39.887269,116.380752)

        print bd_decrypt(39.895748,116.377368)

    if args.get('geocoding2', False):
        lat, lnt = 39.887269,'116.380752'
        results = getAddress(lat, lnt)
        print "-" * 40
        print results

        lat, lnt = 39.887269,'116.380752'
        results = getAddressGoogle(lat, lnt)
        print "-" * 40
        print results

