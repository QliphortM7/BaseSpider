# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from __future__ import unicode_literals
import time
import requests
import re
import json
from bs4 import BeautifulSoup


def get_url_data(crawl_url):
    page_data = get_page(crawl_url)
    json_page_data = json.dumps(page_data, ensure_ascii=False)
    f = open('page_data', 'w', encoding='utf8')
    f.write(json_page_data)
    f.close()


def get_page(crawl_url):
    data_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/86.0.4240.111 Safari/537.36'}
    res = requests.get(crawl_url, headers=headers)
    text = res.text
    soup = BeautifulSoup(text, 'lxml')
    while len(soup.select('div[class="info"]')) != 0:
        temp_data_list = get_data_bs(soup)
        data_list = data_list + temp_data_list
        if len(soup.select('span[class="next"] a')) != 0:
            next_url = 'http://book.douban.com' + soup.select('span[class="next"] a')[0]['href']
            res = requests.get(next_url, headers=headers)
            text = res.text
            soup = BeautifulSoup(text, 'lxml')
        else:
            break
    print("有效数据：" + str(len(data_list)))
    return data_list


# # 使用正则表达式方法
# def get_data(text):
#     text = text.replace('\n', '')
#     pattern = re.compile('<li class="subject-item">.*?<a href="(.*?)" title="(.*?)".*?<div class="pub">('
#                          '.*?)</div>.*?<span class="rating_nums">(.*?)</span>')
#     tuple_list = re.findall(pattern, text)
#     data_list = []
#     for j in range(len(tuple_list)):
#         temp_list = list(tuple_list[j])
#         info_list = temp_list[2].split('/')
#         for i in range(len(info_list)):
#             info_list[i] = info_list[i].strip()
#         temp_list.pop(2)
#         temp_list = temp_list + info_list
#         data_list.append(temp_list)
#     return data_list


# 使用BeautifulSoup方法
def get_data_bs(soup):
    data_list = []
    for item in soup.select('div[class="info"]'):
        info_list = item.select('div[class="pub"]')[0].get_text().split('/')
        for i in range(len(info_list)):
            info_list[i] = info_list[i].strip()
        if len(info_list) < 4:
            return data_list
        rating_nums = item.select('span[class="rating_nums"]')
        temp_dict = {'link': item.find('a')['href'], 'title': re.sub('\\s', '', item.find('a').get_text()),
                     'rate': '评价人数不足' if len(rating_nums) == 0 else rating_nums[0].get_text(),
                     'price': info_list[-1], 'pub_date': info_list[-2], 'press': info_list[-3],
                     'author': ' / '.join(info_list[:-3])}
        data_list.append(temp_dict)
    return data_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start = time.time()
    url = 'https://book.douban.com/tag/%E7%A4%BE%E4%BC%9A%E5%AD%A6?start=0&type=S'
    get_url_data(url)
    end = time.time()
    print("运行时间：" + str(end - start))
