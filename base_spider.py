import time
import json
import xlwt
import tools
import pymysql
import pymysql.cursors
from tools import DBOperation
from concurrent.futures import ThreadPoolExecutor


class BaseSpider(object):

    # 有关tag的英文需要调整
    def __init__(self, tag):
        """Base class to crawl data.
        :param tag:
        """
        self.tag = tag
        self.url = 'https://book.douban.com/tag/{tag}?start={num}&type=T'
        self.craw_executor = ThreadPoolExecutor(max_workers=5)
        pass

    # json格式保存
    @staticmethod
    def save_as_json(page_data):
        json_page_data = json.dumps(page_data, ensure_ascii=False)
        f = open('book_{tag}'.format(tag='politics'), 'w', encoding='utf8')
        f.write(json_page_data)
        f.close()

    # excel格式保存
    def save_as_excel(self, page_data):
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
        book.save('{tag}_page_data.xlsx'.format(tag=tools.baidu_translate(self.tag)))

    # 保存到MySQL数据库
    def save_mysql(self, page_data):
        connection = DBOperation()
        connection.save_to_sql(page_data, self.tag)
