# !/usr/bin/python
# -*- coding:utf-8 -*-
# __author__ = 'MUZI'

import requests
import json
from 高德config import *


def getHeaders():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
        'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
        'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
        'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    ]
    index = random.randrange(0,len(user_agent_list))
    headers = {
        'User-Agent': user_agent_list[index]
    }
    # print (headers)
    return headers

def get_url_html(url):
    try:
        r = requests.get(url,headers=getHeaders())
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print('获取网页HTML，成功')
        return r.text
    except:
        print('获取网页HTML，失败')
        return '获取网页HTML，失败'

def parse_url():
    return None

def geocode(address):
    """
    利用百度geocoding服务解析地址获取位置坐标
    :param address:需要解析的地址
    :return:
    """
    geocoding = {'s': 'rsv3',
                 'key': KEY,
                 'city': '全国',
                 'address': address}
    res = requests.get(
        "http://restapi.amap.com/v3/geocode/geo", params=geocoding)
    print(res.text)
    if res.status_code == 200:
        json = res.json()
        status = json.get('status')
        count = json.get('count')
        if status == '1' and int(count) >= 1:
            geocodes = json.get('geocodes')[0]
            lng = float(geocodes.get('location').split(',')[0])
            lat = float(geocodes.get('location').split(',')[1])
            return [lng, lat]
        else:
            return None,1
    else:
        return None,2

def main():
    url = 'url' # 要请求的url
    html = get_url_text(url)

if __name__ == '__main__':
    # main()
    print(geocode(ADDRESS))




