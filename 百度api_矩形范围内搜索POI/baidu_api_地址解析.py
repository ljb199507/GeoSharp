# !/usr/bin/python
# -*- coding:utf-8 -*-
# __author__ = 'MUZI'
import json
import random
import time
import csv
import pandas
import pymongo
import requests
from baidu_config import *


# 对给定区域内搜索
class BaiDuPOI(object):
    def __init__(self, itemy, scope):
        self.itemy = itemy
        self.scope = scope

    def getHeaders(self):
        user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
            'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
            'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
            'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
        ]
        index = random.randrange(0, len(user_agent_list))
        headers = {
            'User-Agent': user_agent_list[index]
        }
        # print (headers)
        return headers

    def get_url_html(self,url,params):
        try:
            r = requests.get(url, headers=self.getHeaders(),params = params)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            print('获取网页HTML，成功，','现在是第 ',params['page_num'],' 页')
            return r
        except:
            print('获取网页HTML，失败',url)
            with open('erros_log.text','a') as f:
                f.write((params['bounds'],params['page_num'],url))
                f.close()
            return None

    # 对response解析，返回enumerate
    def parse(self):
        for page in range(0,20):
            time.sleep(0.5)
            params = {
                'query': self.itemy,
                # 'region': '长沙市岳麓区',
                'bounds': self.scope,
                'page_siz': 20,
                'page_num': page,
                'output': 'json',
                'ak': BAIDU_KEY,
            }
            url = 'http://api.map.baidu.com/place/v2/search?'
            res = self.get_url_html(url,params).text
            # print(self.get_url_html(url,params).url)

            if res!=None:
                data = json.loads(res)
                if data['total'] != 0:
                    for item in data['results']:
                        json_sel = {}
                        # json_sel['h1'] = h1
                        # json_sel['h2'] = h2
                        json_sel['type'] = self.itemy
                        json_sel['name'] = item["name"]
                        try:
                            json_sel['lat'] = item["location"]["lat"]
                            json_sel['lng'] = item["location"]["lng"]
                        except:
                            json_sel['lat'] = '无数据'
                            json_sel['lng'] = '无数据'
                        json_sel['province'] = item["province"]
                        json_sel['city'] = item["city"]
                        json_sel['area'] = item["area"]
                        try:
                            json_sel['street_id'] = item["street_id"]
                        except:
                            json_sel['street_id'] = '无数据'
                        try:
                            json_sel['telephone'] = item["telephone"]
                        except:
                            json_sel['telephone'] = '无数据'
                        yield json_sel
                else:
                    print('本页及以后无数据')
                    break

    def save_mongodb(self):
        res = self.parse()
        col = ['type', 'province', 'city', 'area', 'name', 'lng', 'lat', 'street_id', 'telephone']
        df = pandas.DataFrame([i for i in res], columns=col)

        my_client = pymongo.MongoClient('MONGO_URL')
        my_db = my_client['MONGO_DB']
        my_col = my_db['MONGO_TABLE']

        my_col.insert_many(df)
        my_client.close()

    def save_csv(self):
        res = self.parse()
        col = ['type','province','city','area','name','lng','lat','street_id','telephone']
        df = pandas.DataFrame([i for i in res],columns=col)
        with open(FILENAME, 'a', encoding='utf_8_sig', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(df.values.tolist())
            csvfile.close()

        # df.to_csv(FILENAME,index=False,sep=',',mode='a',)
        print('------------------------打印成功-------------------------')

def openfile():
    col = ['type', 'province', 'city', 'area', 'name', 'lng', 'lat', 'street_id', 'telephone']
    with open(FILENAME, 'a', encoding='utf_8_sig', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(col)
        csvfile.close()
    return '成功打开文件！！！'

# 对矩形范围内的兴趣点进行分类爬取
def main_jx():
    print("开始爬数据，请稍等...")
    start_time = time.time()

    # 对大的范围进行切割，得到小范围，经纬度的坐标
    scope_div = ScopeDiv(SCOPE,DIVD)
    # ls = scope_div.lnglat_row()     # 老师方法得到的小范围的经纬度坐标list
    scope_s_all = scope_div.lnglat_row_me()    # 我的方法得到的小范围的经纬度坐标list
    # print(scope_s_all[0])

    i = 0
    print(openfile())
    for scope_s in scope_s_all:
        i += 1
        for pois in POIS:
            print('现在正在爬 {}，总共有 {} 个区域要爬取，现在正在爬第 {} 个。'.format(pois,len(scope_s_all),i))
            loc = BaiDuPOI(pois,scope_s)
            # loc.save_mongodb()
            loc.save_csv()

    end_time = time.time()
    print("数据爬取完毕，用时%.2f秒" % (end_time - start_time))

if __name__ == '__main__':
    main_jx()
