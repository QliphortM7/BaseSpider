# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from __future__ import unicode_literals
import requests
import re
from tools import time_delay
from base_spider import BaseSpider
from bs4 import BeautifulSoup


class SessionSpider(BaseSpider):

    def __init__(self, tag):
        """Use requests and BeautifulSoup to crawl data.
        :param tag:
        """
        super().__init__(tag)
        self.session = requests.Session()

    # 使用Requests + BeautifulSoup方式爬取
    # 线程池多线程爬取
    def execute_task(self):
        self.log_in()
        data_list = []
        url_list = [self.url.format(tag=self.tag, num=i * 20) for i in range(50)]
        work_list = self.craw_executor.map(self.get_page, url_list)
        for task_result in work_list:
            data_list = data_list + task_result
        print("完整数据：" + str(len(data_list)))
        self.save_as_json(data_list)

    # 循环获取每一页的书本数据
    @time_delay
    def get_page(self, crawl_url):
        print('开始爬取：' + crawl_url)
        temp_list = []
        soup = self.get_url_soup(crawl_url)
        if len(soup.select('div[class="info"]')) != 0:
            temp_data_list = self.get_book_info(soup)
            if len(temp_data_list) != 0:
                return temp_data_list
            else:
                print(soup.get_text())
        return temp_list

    # 使用BeautifulSoup方法:获取书籍基本信息
    def get_book_info(self, soup):
        info_list = []
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
                         'rate': '评价人数不足' if not rating_nums or rating_nums[0].get_text() == '' else
                         rating_nums[0].get_text(),
                         'evaluators': '0' if not evaluators else evaluators[0],
                         'pub_date': info_list[-2], 'press': info_list[-3], 'author': ' / '.join(info_list[:-3])}
            detail_dict = self.get_detail(item.find('a')['href'])
            temp_dict.update(detail_dict)
            info_list.append(temp_dict)
        return info_list

    # 获取书籍标签、评论数等
    @time_delay
    def get_detail(self, book_url):
        detail_dict = {}
        tag_list = []
        soup = self.get_url_soup(book_url)
        tags = soup.select('a[class="tag"]')
        for item in tags:
            tag_list.append(item.get_text())
        detail_dict['tags'] = ",".join(tag_list)
        comments = soup.select('div[class="mod-hd"] span[class="pl"] a')
        review = soup.select('section[id="reviews-wrapper"] span[class="pl"] a')
        detail_dict['comments'] = re.findall("\\d+", '0' if len(comments) == 0 else comments[0].get_text())[0]
        detail_dict['review'] = re.findall("\\d+", '0' if len(review) == 0 else review[0].get_text())[0]
        return detail_dict

    # 提取一个网页的基本内容
    def get_url_soup(self, target_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/86.0.4240.111 Safari/537.36'}
        res = self.session.get(url=target_url, headers=headers)
        text = res.text
        soup = BeautifulSoup(text, 'lxml')
        return soup

    # 模拟登录
    def log_in(self):
        log_url = 'https://accounts.douban.com/j/mobile/login/basic'
        headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 '
                                 'Firefox/78.0',
                   'Referer': 'https://accounts.douban.com/passport/login?source=book'}
        data = {'ck': '',
                'name': '15866710115',
                'password': 'douban7WaN4QaV',
                'remember': 'false',
                'ticket': ''}
        try:
            res = self.session.post(url=log_url, headers=headers, data=data)
        except Exception as e:
            print(e)


