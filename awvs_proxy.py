__author__ = 'leezp'
# xray 一键分发awvs任务
# 191130
# -*- coding:utf-8 -*-
import requests
import json
import urllib3
import time
import queue

urllib3.disable_warnings()


class define:
    num = 1
    GREEN = "\033[32m"
    RED = "\033[0;31m"
    BLUE = "\033[94m"
    ORANGE = "\033[33m"
    host = "https://127.0.0.1:3443/"  # 端口后面一定要加/
    api_key = "1986ad8c0a5b3df4d7028d5f3c06e936c6ffee1016f8148fc9415805468875fc0"
    api_header = {'X-Auth': api_key, 'content-type': 'application/json;charset=UTF-8'}
    awvs_scan_rule = {
        "full": "11111111-1111-1111-1111-111111111111",
        "highrisk": "11111111-1111-1111-1111-111111111112",
        "XSS": "11111111-1111-1111-1111-111111111116",
        "SQL": "11111111-1111-1111-1111-111111111113",
        "Weakpass": "11111111-1111-1111-1111-111111111115",
        "crawlonly": "11111111-1111-1111-1111-111111111117"
    }


def add(awvshost, url):
    # 添加任务
    data = {"address": url, "description": url, "criticality": "10"}
    try:
        response = requests.post(awvshost + "api/v1/targets", data=json.dumps(data), headers=define.api_header,
                                 timeout=30, verify=False)
        result = json.loads(response.content)
        return result['target_id']
    except Exception as e:
        print(str(e))
        return


def cool(awvshost, addr, port, url):
    try:
        target_id = add(awvshost, url)
    except:
        print(url)
        pass
    try:
        data = {"proxy": {"enabled": True, "address": addr, "protocol": "http", "port": port}}
        response = requests.patch(awvshost + "api/v1/targets/" + target_id + "/configuration", verify=False,
                                  data=json.dumps(data), headers=define.api_header)
        '''
        resp = requests.get(awvshost + "api/v1/targets/" + target_id + "/configuration", data=json.dumps(data),
                            headers=define.api_header)
        print(resp.text)
        '''
        data = {'target_id': target_id, 'profile_id': define.awvs_scan_rule['crawlonly'],
                'schedule': {'disable': False, 'start_date': None, 'time_sensitive': False}}
    except Exception as e:
        print(url)
        pass
    try:
        r = requests.post(url=awvshost + 'api/v1/scans', timeout=10, verify=False, headers=define.api_header,
                          data=json.dumps(data))
        if r.status_code == 201:
            print(define.BLUE + '[-] OK, 扫描任务已经启动 当前扫描第' + str(define.num) + '个网站:%s' % url)
            define.num += 1
    except Exception as e:
        print(e)
        print(url)
        pass


def singlevps():
    s = open('url.txt', 'r')
    k = 0
    j = 0
    for i in s.readlines():
        j += 1
        if j < 1:
            continue
        if k > 123:
            break
        else:
            cool(define.host, "127.1.1.1", 22, i.strip())
            k += 1
            time.sleep(60)


def multivps():
    s = open('url.txt', 'r')

    q = queue.Queue()
    host = {
        1: '172.16.1.1:22,root,XXX,7776'
        , 2: '172.16.1.2:22,root,XXX,7775'
        , 3: '172.16.1.3:22,root,XXX,7776'
        , 4: '172.16.1.4:22,root,XXX,7773'
        , 5: '172.16.1.5:22,root,XXX,7771'
        , 6: '172.16.1.6:22,root,XXX,7778'
        , 7: '172.16.1.7:22,root,XXX,7772'
        , 8: '172.16.1.8:22,root,XXX,7779'
        , 9: '172.16.1.9:22,root,XXX,7770'
        , 10: '172.16.1.10:22,root,XXX,7774'
        , 11: '172.16.1.11:61001,root,XXX,7773'
        , 12: '172.16.1.12:61001,root,XXX,7774'  
    }

    for i in s.readlines():
        # 由 lijiejie子域名 扫描完 分割 ， www.baidu.com   cdn
        q.put(i.split(' ')[0].strip())
    while not q.empty():
        try:
            for k in range(len(host)):
                ip = host.get(k + 1).split(':')[0].strip()
                port = host.get(k + 1).split(',')[-1].strip()
                if not q.empty():
                    cool(define.host, ip, port, q.get())
                else:
                    print('运行结束')
                    break
            time.sleep(10)
        except:
            print('运行结束')


if __name__ == '__main__':
    # singlevps()
    multivps()
