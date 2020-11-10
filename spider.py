# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from __future__ import unicode_literals
import time
import random
import requests
import re
import json
import xlwt
import pymysql
import pymysql.cursors
from bs4 import BeautifulSoup

global n

s = requests.Session()


def get_url_data(crawl_url):
    s, r = log_in()
    page_data = get_page(crawl_url)
    save_as_json(page_data)
    save_mysql(page_data)


# 循环获取每一页的书本数据
def get_page(crawl_url):
    global n
    n = 0
    data_list = []
    soup = get_url_soup(crawl_url)
    while len(soup.select('div[class="info"]')) != 0:
        temp_data_list = get_data_bs(soup)
        print("当前爬取数：" + str(n))
        if len(temp_data_list) != 0:
            data_list = data_list + temp_data_list
        if len(soup.select('span[class="next"] a')) != 0:
            next_url = 'http://book.douban.com' + soup.select('span[class="next"] a')[0]['href']
            soup = get_url_soup(next_url)
        else:
            print(soup.get_text())
            break
    print("完整数据：" + str(len(data_list)))
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


# 使用BeautifulSoup方法:获取书籍基本信息
def get_data_bs(soup):
    global n
    data_list = []
    for item in soup.select('div[class="info"]'):
        info_list = item.select('div[class="pub"]')[0].get_text().split('/')
        for i in range(len(info_list)):
            info_list[i] = info_list[i].strip()
        if len(info_list) < 4:
            print("非完整信息：" + "/".join(info_list))
            continue
        rating_nums = item.select('span[class="rating_nums"]')
        evaluators = re.findall('\\d+', item.select('span[class="pl"]')[0].get_text())
        temp_dict = {'link': item.find('a')['href'], 'title': re.sub('\\s', '', item.find('a').get_text()),
                     'rate': '评价人数不足' if len(rating_nums) == 0 or rating_nums[0].get_text() == '' else
                     rating_nums[0].get_text(),
                     'evaluators': '0' if len(evaluators) == 0 else evaluators[0],
                     'pub_date': info_list[-2], 'press': info_list[-3], 'author': ' / '.join(info_list[:-3])}
        time.sleep(random.random())
        detail_dict = get_detail(item.find('a')['href'])
        temp_dict.update(detail_dict)
        data_list.append(temp_dict)
        n += 1
    return data_list


# 获取书籍标签、评论数等
def get_detail(book_url):
    detail_dict = {}
    tag_list = []
    soup = get_url_soup(book_url)
    tags = soup.select('a[class="tag"]')
    for item in tags:
        tag_list.append(item.get_text())
    detail_dict['tags'] = ",".join(tag_list)
    comments = soup.select('div[class="mod-hd"] span[class="pl"] a')
    review = soup.select('section[id="reviews-wrapper"] span[class="pl"] a')
    detail_dict['comments'] = re.findall("\\d+", '0' if len(comments) == 0 else comments[0].get_text())[0]
    detail_dict['review'] = re.findall("\\d+", '0' if len(review) == 0 else review[0].get_text())[0]
    return detail_dict


# json格式保存
def save_as_json(page_data):
    json_page_data = json.dumps(page_data, ensure_ascii=False)
    f = open('page_data', 'w', encoding='utf8')
    f.write(json_page_data)
    f.close()


# excel格式保存
def save_as_excel(page_data, title):
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 0, '名称')
    sheet.write(0, 1, '链接')
    sheet.write(0, 2, '评分')
    sheet.write(0, 3, '评价人数')
    sheet.write(0, 4, '作者')
    sheet.write(0, 5, '出版社')
    sheet.write(0, 6, '出版日期')
    sheet.write(0, 7, '标签')
    sheet.write(0, 8, '短评数')
    sheet.write(0, 9, '书评数')
    for i in range(len(page_data)):
        sheet.write(i + 1, 0, page_data[i]['title'])
        sheet.write(i + 1, 1, page_data[i]['link'])
        sheet.write(i + 1, 2, page_data[i]['rate'])
        sheet.write(i + 1, 3, page_data[i]['evaluators'])
        sheet.write(i + 1, 4, page_data[i]['author'])
        sheet.write(i + 1, 5, page_data[i]['press'])
        sheet.write(i + 1, 6, page_data[i]['pub_date'])
        sheet.write(i + 1, 7, page_data[i]['tags'])
        sheet.write(i + 1, 8, page_data[i]['comments'])
        sheet.write(i + 1, 9, page_data[i]['review'])
    book.save(title)


# 保存到MySQL数据库
def save_mysql(page_data):
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='8281',
                           db='spider_book_data',
                           charset='utf8mb4')
    try:
        with conn.cursor() as cursor:
            for item in page_data:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                sql = "INSERT INTO spider_book_data.psychology_book_data(`title`,`link`,`rate`,`evaluators`,`author`," \
                      "`press`,`pub_date`,`tags`,`comments`,`review`,`create_time`) " \
                      "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                params = (item['title'], item['link'], item['rate'], item['evaluators'], item['author'], item['press'],
                          item['pub_date'], item['tags'], item['comments'], item['review'], current_time)
                cursor.execute(sql, params)
                conn.commit()
    except Exception:
        conn.rollback()
    cursor.close()
    conn.close()


# 提取一个网页的基本内容
def get_url_soup(target_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/86.0.4240.111 Safari/537.36'}
    res = s.get(target_url, headers=headers)
    text = res.text
    soup = BeautifulSoup(text, 'lxml')
    return soup


# 模拟登录
def log_in():
    url = 'https://accounts.douban.com/j/mobile/login/basic'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/86.0.4240.111 Safari/537.36',
               'Referer': 'https://accounts.douban.com/passport/login?source=book'}
    data = {'ck': '',
            'name': '15866710115',
            'password': 'douban7WaN4QaV',
            'remember': 'false',
            'ticket': ''}
    r = []
    try:
        r = s.post(url, headers=headers, data=data)
    except Exception as e:
        print(e)
    return s, r
