# -*- coding:utf-8 -*-
__author__ = 'leezp'
__date__ = 20191231
import asyncio
import aiohttp
import aiomultiprocess
import aiofiles
import queue
import datetime
import random
from lxml import etree
import urllib3
import UA_Pool as UApool
import re
import argparse

urllib3.disable_warnings()

class Gun():
    def __init__(self):
        self.dic = {
            "None": [
            ],
            "taobao": [
                ('//*[@id="error-notice"]/div[2]/div[1]   :)  没有找到相应的店铺信息',
                 '//*[@id="error-notice"]/div[2]/div[3]/ol/li[4]   :) 五秒后跳转至'),
                '/html/body/div/div/p[2]  :) 很抱歉',  # ！暂时无法处理您的请求,
                '/html/body/div/div/p[2]  :) 亲，慢慢来，请先坐下来喝口水！',
                '//*[@id="err"]/div[1]/p[1] :) 亲，小二正忙，滑动一下马上回来',
                '//*[@id="dead-page"]/header/div/div/div[2]/p  :) 亲，这是个机器人猖狂的时代，请进行验证证明咱是正常人~',
                '//*[@id="dead-page"]/header/div/div/div[2]/div[2]/p[1]  :) 抱歉',  # 很抱歉，现在暂时无法处理您的请求
                '//*[@id="J_4938560545"]/div/div[1]/h2  :) 很抱歉，您查看的页面找不到了！',
                '//*[@id="err"]/div[1]/p  :)  抱歉！',  # 页面无法访问……
                '//*[@id="content"]/div[1]/div/div/div[2]/div[1]/h3/em[2]   :) 抱歉，您要访问的页面不存在',
                '//*[@id="App"]/div/div/div/div/div[2]/div[2]   :) 内网访问受限，请先登录阿里郎连接内网后再试',
				'/html/body/div[5]/h4  :)  亲，店铺不存在哟！', #亲，店铺不存在哟！输入的店铺地址不正确或店铺已经关闭。
				'/html/body/div[2]/div/dl/dt/p  :)   当前页面访问人数过多'
            ]
        }
        self.asyncio_Semaphore = 500  # 设置最大并发数为500 , linux可设置1000，效率翻倍
        self.title_regex = re.compile(r'<title>([\s\S]*?)</title>')
        self.zh_regex = re.compile(r'[\u4e00-\u9fa5]+')


def parse_args():
    parse = argparse.ArgumentParser(usage='python36 %(prog)s -f targetUrl_full.txt')
    parse.add_argument('-f', dest='input_file', type=str, default='url_full.txt', help='default is url_full.txt')
    arg = parse.parse_args()
    return arg.input_file


# input_file = 'alisports.com_1_full.txt'
input_file = parse_args()
name = input_file.split('_')[0].strip()
switch = False
for key, value in Gun().dic.items():
    if key == name:
        dic_key = name
        switch = True
        break
if switch == False:
    dic_key = "None"
output_file = name + '_out.txt'
List = Gun().dic["None"]
output_file = name + '_out.txt'

q = queue.Queue()
file = open(input_file, encoding='utf-8')
for x in file.readlines():
    #url = 'http://' + x.split(' ')[0].strip()
    url = x.split(' ')[0].strip()
    q.put(url)


# 淘宝 约124 次出现验证码
async def fetch(url):
    sem = asyncio.Semaphore(Gun().asyncio_Semaphore)
    async with sem:
        # 最大访问数
        async with aiohttp.ClientSession() as session:
            try:
                # proxy="http://ip:port"
                async with session.get(url, headers={'User-Agent': random.choice(UApool.data)},
                                       verify_ssl=False,
                                       timeout=3) as resp:
                    # If encoding is None content encoding is autocalculated using Content-Type HTTP header and chardet tool if the header is not provided by server.
                    #  text=await resp.text(encoding=None, errors='ignore') 等价于 content = await  resp.read()  code=chardet.detect(content)['encoding']   text=await resp.text(encoding=code, errors='ignore')
                    status = resp.status
                    text = await resp.text(encoding=None, errors='ignore')
                    if Gun().title_regex.search(text) and Gun().title_regex.search(text).group(1):
                        s = Gun().title_regex.search(text).group(1).strip()
                        if (
                                u'旗舰店' in s and u'天猫' in s) or u'理想生活上天猫' in s or u'现在暂时无法处理您的请求' in s or \
                                u'大麦' in s or u'全球演出赛事官方购票平台' or u'亲，访问受限了' in s or \
                                'security-X5' in s or 'dopa.com' in s or '米聊' in s or u'官方旗舰店' in s:
                            return
                    html = etree.HTML(text)
                    xp = {}
                    for i in range(len(List)):
                        if type(List[i]).__name__ == "tuple":
                            xp[str(i)] = html.xpath(List[i][0].split(':)')[0].strip())
                            xp["100"] = html.xpath(List[i][1].split(':)')[0].strip())
                        else:
                            xp[str(i)] = html.xpath(List[i].split(':)')[0].strip())
                    for i in range(len(List)):
                        if type(List[i]).__name__ == "tuple":
                            if len(xp[str(i)]) > 0 and len(xp[str("100")]) > 0:
                                if xp[str(i)][0].text.strip() == List[i][0].split(':)')[-1].strip() and xp[
                                    "100"][0].text.strip() == List[i][1].split(':)')[-1].strip():
                                    return
                        elif len(xp[str(i)]) > 0 and xp[str(i)][0].text:
                            if List[i].split(':)')[-1].strip() in xp[str(i)][0].text.strip():
                                return
                    async with aiofiles.open(output_file, 'a', encoding='utf-8') as f:
                        # await f.write("{}  {}  {}".format(url, status, text) + '\n')
                        await f.write("{}  {}".format(url, status) + '\n')
                        await f.close()
            except Exception as e:
                print(e)
                pass
            finally:
                print('test speed')


async def main():
    tasks = []
    while not q.empty():
        url = q.get()
        tasks.append(url)
    async with aiomultiprocess.Pool() as pool:
        result = await pool.map(fetch, tasks)
        # print(result)


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(start_time)
    # event_loop事件循环：程序开启一个无限的循环，当把一些函数注册到事件循环上时，满足事件发生条件即调用相应的函数。
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end_time = datetime.datetime.now()
    print('消耗时间:{}'.format(end_time - start_time))
