import re
import json
import logging
from base_spider import BaseSpider
from tools import time_delay
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class SeleniumSpider(BaseSpider):

    def __init__(self, tag):
        """Use Selenium to crawl data.
        :param tag:
        """
        super().__init__(tag)

    def execute_task(self):
        data_list = []
        url_list = [self.url.format(tag=self.tag, num=i * 200) for i in range(5)]
        work_list = self.craw_executor.map(self.get_page, url_list)
        for task_result in work_list:
            data_list = data_list + task_result
        print("完整数据：" + str(len(data_list)))
        if data_list:
            self.save_as_json(data_list)

    def get_page(self, crawl_url):
        full_list = []
        driver = CrawlBrowser()
        try:
            for i in range(10):
                index = re.findall("start=(\\d+)", crawl_url)[0]
                replace_index = 'start=' + str(int(index) + i*20)
                url = re.sub('start=(\\d+)', replace_index, crawl_url)
                temp_list = self.get_book_info(driver, url)
                full_list = full_list + temp_list
        except Exception as e:
            print("Exception occur: ")
            logging.exception(e)
        finally:
            driver.close()
        return full_list

    def get_book_info(self, driver, target_url):
        print('开始爬取：' + target_url)
        info_list = []
        driver.get_url(target_url)
        items = driver.find_elements('div .info')
        for item in items:
            info_txt = item.find_element_by_css_selector('.pub').text
            info_dict = self.process_info(info_txt)
            if not info_dict:
                print("非完整信息：", info_txt)
                continue
            evaluates = re.findall('\\d+', item.find_element_by_css_selector('.pl').text)
            temp_dict = {'link': item.find_element_by_css_selector('a').get_attribute('href'),
                         'title': item.find_element_by_css_selector('a').text,
                         'rate': self.get_select_value(item, '.rating_nums', '评价人数不足'),
                         'evaluators': evaluates[0] if evaluates else 10}
            temp_dict |= info_dict
            info_list.append(temp_dict)
        for temp_dict in info_list:
            detail_url = temp_dict['link']
            driver.get_url(detail_url)
            detail_dict = self.get_detail(driver)
            temp_dict |= detail_dict
        return info_list

    def get_detail(self, driver):
        detail_dict = {}
        tags_text = driver.find_element('#db-tags-section .indent').text
        detail_dict['tags'] = re.sub('\\s+', ',', tags_text.strip())
        comments_ele = self.get_select_value(driver.browser, '.mod-hd .pl a', '0')
        reviews_ele = self.get_select_value(driver.browser, '#reviews-wrapper .pl a', '0')
        detail_dict['comments'] = re.findall('\\d+', comments_ele)[0]
        detail_dict['review'] = re.findall('\\d+', reviews_ele)[0]
        return detail_dict

    @staticmethod
    def get_select_value(driver, element, default_value):
        try:
            value = driver.find_element_by_css_selector(element).text
            return value if value else default_value
        except NoSuchElementException:
            return default_value

    # 调整标题，一次性
    @staticmethod
    def get_title(driver, target_url):
        print('开始爬取：' + target_url)
        title_list = []
        driver.get_url(target_url)
        items = driver.find_elements('div .info')
        for item in items:
            temp_list = [i.strip() for i in item.find_element_by_css_selector('.pub').text.split('/')]
            if len(temp_list) < 4:
                print('非完整信息')
                continue
            temp_dict = {'link': item.find_element_by_css_selector('a').get_attribute('href'),
                         'title': item.find_element_by_css_selector('a').text}
            title_list.append(temp_dict)
        return title_list

    # 调整标题，一次性
    @staticmethod
    def adjust_title(data_list):
        ex_dict = {}
        ex_book_dict = {}
        for d in data_list:
            ex_book_dict[d['link']] = d['title']
        with open('book_philosophy', 'r', encoding='utf8') as f:
            full_list = json.load(f)
        for d in full_list:
            ex_dict[d['link']] = d
        for key in ex_book_dict.keys():
            ex_dict[key]['title'] = ex_book_dict[key]
        ex_list = []
        for d in ex_dict.values():
            ex_list.append(d)
        with open('book_philosophy', 'w', encoding='utf8') as f:
            json.dump(ex_list, f, ensure_ascii=False)

    @staticmethod
    def process_info(txt):
        dic = {}
        pt = re.compile('\\d{4}')
        wd_list = txt.split(' / ')
        s = pt.search(txt)
        if len(wd_list) < 4:
            return dic
        elif not s:
            dic = {"name": "/".join(wd_list[:-2]), " press": wd_list[-2], "pub_date": ""}
        elif pt.search(wd_list[-1]):
            dic = {"name": "/".join(wd_list[:-2]), " press": wd_list[-2], "pub_date": wd_list[-1]}
        elif pt.search(wd_list[-2]):
            dic = {"name": "/".join(wd_list[:-3]), " press": wd_list[-3], "pub_date": wd_list[-2]}
        return dic


class CrawlBrowser(object):

    def __init__(self):
        """Create Chrome browser and login to execute task.
        """
        options = Options()
        options.add_argument('-headless')
        self.path = "C:\\Users\\weimaoquan\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe"
        self.browser = webdriver.Chrome(executable_path=self.path, options=options)
        self.browser.implicitly_wait(3)
        self.login()

    @time_delay
    def login(self):
        self.browser.get('https://accounts.douban.com/passport/login')
        self.browser.find_element_by_css_selector('.account-tab-account').click()
        self.browser.find_element_by_css_selector("input[id='username']").send_keys('15866710115')
        self.browser.find_element_by_css_selector("input[id='password']").send_keys('douban7WaN4QaVM7')
        self.browser.find_element_by_css_selector("input[id='password']").send_keys(Keys.ENTER)

    @property
    def page_source(self):
        return self.browser.page_source

    @time_delay
    def get_url(self, url):
        return self.browser.get(url)

    def find_element(self, pattern):
        return self.browser.find_element_by_css_selector(pattern)

    def find_elements(self, pattern):
        return self.browser.find_elements_by_css_selector(pattern)

    def close(self):
        self.browser.close()
