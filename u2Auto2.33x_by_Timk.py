# -*- coding:utf-8 -*-
# !/usr/bin/env python3

'''
Original Author: ayasakinagi
Original Author Email: xyz.wang@outlook.com
Author:Timk
Email:i@itkmo.cn

primarily includes the following modifications: Customized the functionality to release global magic spells of ↓0.00x↑2.33x within a specified time frame. Any spells exceeding that timeframe are automatically released as restoration magic spells of ↓0.00x.

环境: Python3
依赖: requests, beautifulsoup4, lxml, sys, threading
使用: 修改uid, cookie(需要保留nexusphp_u2=), utime, uploadTimeInterval, sleeptime, interval变量
apt install python3 python3-pip screen
pip3 install requests beautifulsoup4 lxml

nano /etc/systemd/system/u2Auto233.service
-----------------------------------------------
[Unit]
Description=u2Auto233 By_Timk Service
After=network.target

[Service]
Type=forking
ExecStart=/usr/bin/screen -S u2Auto233_By_Timk -fa -d -m /usr/bin/python3 /root/DelugeScript/u2Auto2.33x_byTimk.py
User=root

[Install]
WantedBy=multi-user.target
-----------------------------------------------
systemctl enable u2Auto233.service
systemctl start u2Auto233.service
'''

import re
import sys
import time
import logging
import requests
import threading
from local_module import get_config
from bs4 import BeautifulSoup as BS
from logging.handlers import RotatingFileHandler

(
    uid, cookie, uploadTimeInterval, sleeptime, interval, rule1_user, rule1_user_other, rule1_start,
    rule1_hours, rule1_promotion, rule1_ur, rule1_dr, rule1_comment, rule2_user, rule2_user_other, rule2_start,
    rule2_hours, rule2_promotion, rule2_ur, rule2_dr, rule2_comment, http_proxy_state, http_proxy_http,
    http_proxy_https
    )= get_config()

proxies = {
    "http": http_proxy_http,
    "https": http_proxy_https,
}

logPath = './u2.33x.log'

header = {
    'dnt': '1',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'zh-CN,zh;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'cache-control': 'max-age=0',
    'authority': 'u2.dmhy.org',
    'cookie': cookie
}

# init log
handler1 = RotatingFileHandler(logPath, maxBytes=100*1024, backupCount=5)  # 日志文件最多100k，保留5个历史日志
handler2 = logging.StreamHandler()
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'

formatter = logging.Formatter(fmt)
handler1.setFormatter(formatter)
handler2.setFormatter(formatter)

logger = logging.getLogger('log')
logger.addHandler(handler1)
logger.addHandler(handler2)
logger.setLevel(logging.DEBUG)

logger.info("Start Cap")

# get ucoinNum
def getUcoinNum():
    url = 'https://u2.dmhy.org/userdetails.php?id=' + str(uid)
    if http_proxy_state == True:
        page = requests.get(url, headers=header, proxies=proxies).text
    elif http_proxy_state == False:
        page = requests.get(url, headers = header).text
    else:
        logger.error('请检查代理设置是否正确 True or False')
    soup = BS(page, 'lxml')
    ucoinNum = soup.find_all('span', {'class': 'ucoin-notation'})[1]['title']
    return ucoinNum
  
def main():
    # Get downloading torrent

    url = 'https://u2.dmhy.org/getusertorrentlistajax.php?userid=' + uid + '&type=leeching'

    if http_proxy_state == True:
        response = requests.get(url, headers=header, proxies=proxies)
    elif http_proxy_state == False:
        response = requests.get(url, headers=header)
    else:
        logger.error('请检查代理设置是否正确 True or False')

    page = response.text
    
    if response.status_code != 200:
        logger.error('Please Check You Network')

    #logger.info('Get downloading torrent page success')
    
    soup = BS(page, 'lxml')
    
    if soup.find('p', string="Access Denied!"):
        logger.error('Access Denied! Please Check You Cookie')
        sys.exit()
        
    td = soup.find('table', {'border': 1}).children
    idList = []
    #id = None
    #uploadRatio = None
    #downloadRatio = None
    for i in td: 
        i = str(i)
        # check 2x, pro_custom为自定义, pro_free2up为2xfree, pro_2up为2x, pro_50pctdown2up为2x 50%off
        if 'pro_free2up' in i:
            continue
        elif 'pro_2up' in i or 'pro_50pctdown2up' in i:
            # get id
            rg = re.compile('id=*?(\\d+)', re.IGNORECASE | re.DOTALL).search(i)
            if rg:
                id = int(rg.group(1))
                idList.append(id)
        elif 'pro_custom' in i:
            # get id
            rg = re.compile('id=*?(\\d+)', re.IGNORECASE | re.DOTALL).search(i)
            if rg:
                id = int(rg.group(1))
            # get uploadRatio
            rg = re.compile('arrowup.*?<b>([+-]?\\d*\\.\\d+)(?![-+0-9\\.])', re.IGNORECASE | re.DOTALL).search(i)
            if rg:
                uploadRatio = float(rg.group(1))
            # get downloadRatio
            rg = re.compile('arrowdown.*?([+-]?\\d*\\.\\d+)(?![-+0-9\\.])', re.IGNORECASE | re.DOTALL).search(i)
            if rg:
                downloadRatio = float(rg.group(1))
            #logger.info('download_id=' + str(id) + ' uploadRatio=' + str(uploadRatio) + ' downloadRatio=' + str(downloadRatio))
            # add id into list
            #if uploadRatio and uploadRatio < 2:
            if downloadRatio != 0:
                idList.append(id)

    # check add time
    idList_1 = []
    idList_2 = []
    for i in idList:
        url = 'https://u2.dmhy.org/details.php?id=' + str(i)
        if http_proxy_state == True:
            page = requests.get(url, headers = header, proxies=proxies).text
        elif http_proxy_state == False:
            page = requests.get(url, headers = header).text
        else:
            logger.error('请检查代理设置是否正确 True or False')
        soup = BS(page, 'lxml')
        uploadTime = time.strptime(soup.find('time')['title'], '%Y-%m-%d %H:%M:%S')
        uploadTimeUTC = time.mktime(uploadTime) - 28800
        # localtimeUTC = time.time() + time.timezone
        localtimeUTC = time.mktime(time.gmtime())
        diff = localtimeUTC - uploadTimeUTC
        if diff <= uploadTimeInterval:
            idList_1.append(i)
        if diff > uploadTimeInterval:
            idList_2.append(i)
        time.sleep(2)
    
    if idList_1:
        logger.info('Need ↓0.00x ↑2.33x: ' + str(idList_1))
    if idList_2:
        logger.info('Need ↓0.00x: ' + str(idList_2))

    # Get magic page 1
    for i in idList_1:
        # get form data
        url = 'https://u2.dmhy.org/promotion.php?action=magic&torrent=' + str(i)
        if http_proxy_state == True:
            page = requests.get(url, headers = header, proxies=proxies).text
        elif http_proxy_state == False:
            page = requests.get(url, headers = header).text
        else:
            logger.error('请检查代理设置是否正确 True or False')
        soup = BS(page, 'lxml')
        data = {}
        data['action'] = soup.find('input', {'name': 'action'})['value']
        data['divergence'] = soup.find('input', {'name': 'divergence'})['value']
        data['base_everyone'] = soup.find('input', {'name': 'base_everyone'})['value']
        data['base_self'] = soup.find('input', {'name': 'base_self'})['value']
        data['base_other'] = soup.find('input', {'name': 'base_other'})['value']
        data['torrent'] = soup.find('input', {'name': 'torrent'})['value']
        data['tsize'] = soup.find('input', {'name': 'tsize'})['value']
        data['ttl'] = soup.find('input', {'name': 'ttl'})['value']

        data['user'] = rule1_user
        data['user_other'] = rule1_user_other
        data['start'] = rule1_start
        data['hours'] = rule1_hours
        data['promotion'] = rule1_promotion
        data['ur'] = rule1_ur
        data['dr'] = rule1_dr
        data['comment'] = rule1_comment
        url = 'https://u2.dmhy.org/promotion.php?test=1'
        if http_proxy_state == True:
            page = requests.post(url, headers = header, data = data, proxies=proxies).text
        elif http_proxy_state == False:
            page = requests.post(url, headers = header, data = data).text
        else:
            logger.error('请检查代理设置是否正确 True or False')
        soup = BS(page, 'lxml')
        ucoinCost = soup.find('span', {'class': '\\"ucoin-notation\\"'})['title'][2:-2]
        logger.info('Torrent ' + str(i) + "'s ucoinCost: " + ucoinCost + ', now your ucoin num is ' + getUcoinNum())

        # Magic
        url = 'https://u2.dmhy.org/promotion.php?action=magic&torrent=' + str(i)
        if http_proxy_state == True:
            page = requests.post(url, headers = header, data = data, proxies=proxies)
        elif http_proxy_state == False:
            page = requests.post(url, headers = header, data = data)
        else:
            logger.error('请检查代理设置是否正确 True or False')
        if page.status_code == 200:
            logger.info('Torrent ' + str(i) + ' ↓0.00x ↑2.33x success, now your ucoin num is ' + getUcoinNum())
        else:
            logger.info('Error, try again later')
    
    # Get magic page 2
    for i in idList_2:
        # get form data
        url = 'https://u2.dmhy.org/promotion.php?action=magic&torrent=' + str(i)
        if http_proxy_state == True:
            page = requests.get(url, headers = header, proxies=proxies).text
        elif http_proxy_state == False:
            page = requests.get(url, headers = header).text
        else:
            logger.error('请检查代理设置是否正确 True or False')

        soup = BS(page, 'lxml')
        data = {}
        data['action'] = soup.find('input', {'name': 'action'})['value']
        data['divergence'] = soup.find('input', {'name': 'divergence'})['value']
        data['base_everyone'] = soup.find('input', {'name': 'base_everyone'})['value']
        data['base_self'] = soup.find('input', {'name': 'base_self'})['value']
        data['base_other'] = soup.find('input', {'name': 'base_other'})['value']
        data['torrent'] = soup.find('input', {'name': 'torrent'})['value']
        data['tsize'] = soup.find('input', {'name': 'tsize'})['value']
        data['ttl'] = soup.find('input', {'name': 'ttl'})['value']

        data['user'] = rule2_user
        data['user_other'] = rule2_user_other
        data['start'] = rule2_start
        data['hours'] = rule2_hours
        data['promotion'] = rule2_promotion
        data['ur'] = rule2_ur
        data['dr'] = rule2_dr
        data['comment'] = rule2_comment
        url = 'https://u2.dmhy.org/promotion.php?test=1'
        if http_proxy_state == True:
            page = requests.post(url, headers = header, data = data, proxies=proxies).text
        elif http_proxy_state == False:
            page = requests.post(url, headers = header, data = data).text
        else:
            logger.error('请检查代理设置是否正确 True or False')
        soup = BS(page, 'lxml')
        ucoinCost = soup.find('span', {'class': '\\"ucoin-notation\\"'})['title'][2:-2]
        logger.info('Torrent ' + str(i) + "'s ucoinCost: " + ucoinCost + ', now your ucoin num is ' + getUcoinNum())

        # Magic
        url = 'https://u2.dmhy.org/promotion.php?action=magic&torrent=' + str(i)
        if http_proxy_state == True:
            page = requests.post(url, headers = header, data = data, proxies=proxies)
        elif http_proxy_state == False:
            page = requests.post(url, headers = header, data = data)
        else:
            logger.error('请检查代理设置是否正确 True or False')
        if page.status_code == 200:
            logger.info('Torrent ' + str(i) + ' ↓0.00x success, now your ucoin num is ' + getUcoinNum())
        else:
            logger.info('Error, try again later')

def log_regularly(interval):
    """定期记录日志的函数。"""
    last_log_time = time.time()
    while True:
        current_time = time.time()
        if current_time - last_log_time >= interval:
            logger.info("u2Auto2.33 Run OK")
            last_log_time = current_time
        time.sleep(interval)  # 每次检查间隔interval秒
        
# 创建一个线程专门用于记录日志
log_thread = threading.Thread(target=log_regularly, args=(60,))
log_thread.daemon = True  # 设置为守护线程，确保主程序退出时线程也会退出
log_thread.start()

if __name__ == '__main__':
    last_log_time = time.time()  # 记录循环开始的时间
    while True:
        try:
            main()
        except Exception as e:
            if str(e) != "'NoneType' object has no attribute 'children'":
                logger.error(e)
                # 如果错误不匹配，则重新抛出异常
        time.sleep(sleeptime)  # 根据需要休眠