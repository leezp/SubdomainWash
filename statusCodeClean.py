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

def parse_args():
    parse = argparse.ArgumentParser(usage='python36 %(prog)s -f url_full.txt')
    parse.add_argument('-f', dest='input_file', type=str, default='url_full.txt', help='default is url_full.txt')
    arg = parse.parse_args()
    return arg.input_file

asyncio_Semaphore = 500  # 设置最大并发数为500 , linux可设置1000，效率翻倍
input_file, dic_key = parse_args()
name = input_file.split('_')[0].strip()
output_file = name + '_1_full.txt'
q = queue.Queue()
file = open(input_file, encoding='utf-8')
for x in file.readlines():
    url = 'http://' + x.split(' ')[0].strip()
    # url = x.split(' ')[0].strip()
    q.put(url)


urllib3.disable_warnings()

async def fetch(url):
    sem = asyncio.Semaphore(asyncio_Semaphore)
    async with sem:
        # 最大访问数
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(url, timeout=5) as response:
                    status = response.status
                    if status == 404 or status == 500 or status == 504 or status == 503 or status == 512 or status == 608 or status == 403:
                        return
                    async with aiofiles.open(output_file, 'a', encoding='utf-8') as f:
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


# asyncio内部用到了select，而select就是系统打开文件数是有限度的，这个其实是操作系统的限制，linux打开文件的最大数默认是1024，windows默认是509，超过了这个值，程序就开始报错
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print(start_time)
    # event_loop事件循环：程序开启一个无限的循环，当把一些函数注册到事件循环上时，满足事件发生条件即调用相应的函数。
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end_time = datetime.datetime.now()
    print('消耗时间:{}'.format(end_time - start_time))
