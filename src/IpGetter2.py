import urllib.request as urllib
import re
import json


def get_page_source(url):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Connection': 'keep-alive',
        'Referer': 'http://www.baidu.com/'
    }
    req = urllib.Request(url, None, headers)
    response = urllib.urlopen(req)
    page_source = response.read()
    return page_source


def get_ipify_org():
    pageObj = get_page_source('https://api.ipify.org/?format=json').decode(
        'utf-8')
    obj = json.loads(pageObj)
    return str(obj['ip'])

def get_ipip_net():
    pageObj = get_page_source('https://www.ipip.net/ip/').decode('utf-8')
    if (pageObj == None):
        return None
    page = str(pageObj)
    result = re.search(r'/ip/(\d+\.\d+\.\d+\.\d+)\.html', page)
    if (result):
        result = re.search(r'\d+\.\d+\.\d+\.\d+', str(result))
        if (result):
            return str(result.group())
    return None


def get_win7sky_com():
    pageObj = get_page_source('https://win7sky.com/ip/')
    if (pageObj == None):
        return None
    page = str(pageObj)
    result = re.search(r'\d+\.\d+\.\d+\.\d+', page)
    if (result):
        return str(result.group())
    return None


def get_ggbing_com():
    pageObj = get_page_source('http://www.ggbing.com/ip/')
    if (pageObj == None):
        return None
    page = str(pageObj)
    result = re.search(r'\d+\.\d+\.\d+\.\d+', page)
    if (result):
        return str(result.group())
    return None

def get_net_cn():
    pageObj = get_page_source(
        'http://www.net.cn/static/customercare/yourip.asp')
    if (pageObj == None):
        return None
    page = str(pageObj)
    result = re.search(r'\d+\.\d+\.\d+\.\d+', page)
    if (result):
        return str(result.group())
    return None

def get_sz_bendibao():
    pageObj = get_page_source('http://sz.bendibao.com/ip/')
    if (pageObj == None):
        return None
    page = str(pageObj)
    result = re.search(r'\d+\.\d+\.\d+\.\d+', page)
    if (result):
        return str(result.group())
    return None

ipList = [
    get_ipify_org,
    get_ipip_net,
    get_win7sky_com,
    get_ggbing_com,
    get_net_cn,
    get_sz_bendibao,
]

def getIpList():
    return ipList

if __name__ == '__main__':
    for getter in getIpList():
        ip = getter()
        print(type(ip), ip)