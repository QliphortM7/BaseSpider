import json
import pymysql
import time
import logging
import random
import hashlib
import requests
from functools import wraps
from dbutils.persistent_db import PersistentDB


class DBPool(object):

    def __init__(self):
        """Provide db pool to connect with database.
        """
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '8281',
            'db': 'spider_book_data',
            'charset': 'utf8mb4'}
        self.db_pool = PersistentDB(pymysql, maxusage=1000, **self.config)

    def db_transaction(self, func):
        @wraps(func)
        def wrapper_func(*args):
            conn = self.db_pool.connection()
            try:
                return func(*args, connection=conn)
            except Exception as e:
                logging.error("发生异常：" + str(e))
                conn.rollback()
            finally:
                conn.close()

        return wrapper_func


class DBOperation(object):

    _INSERT_SQL = "INSERT IGNORE INTO spider_book_data.book_info(`title`,`link`,`rate`,`evaluators`," \
                  "`author`,`press`,`pub_date`,`tags`,`comments`,`review`,`create_time`) " \
                  "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    _UPDATE_SQL = "UPDATE spider_book_data.book_info SET `category` = (CASE WHEN `category` IS NULL " \
                  "THEN %(category)s ELSE CONCAT_WS(',', `category`, %(category)s) END) WHERE `link`=%(link)s "

    _UPDATE_TITLE_SQL = "UPDATE spider_book_data.book_info SET `title`=%(title)s WHERE `link`=%(link)s AND " \
                        "`create_time`>'2020-12-29' "

    _db_pool = DBPool()

    def __init__(self):
        """Manipulate database data.
        """
        pass

    # 将数据导入MYSQL中
    @_db_pool.db_transaction
    def save_to_sql(self, book_data, category, **kwargs):
        if isinstance(book_data, str):
            with open(book_data, 'r', encoding='utf8') as f:
                load_data = json.load(f)
        elif isinstance(book_data, list):
            load_data = book_data
        else:
            raise TypeError("输入类型错误")
        conn = kwargs['connection']
        with conn.cursor() as cursor:
            for item in load_data:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                insert_params = (
                    item['title'], item['link'], item['rate'], item['evaluators'], item['author'],
                    item['press'],
                    item['pub_date'], item['tags'], item['comments'], item['review'], current_time)
                cursor.execute(self._INSERT_SQL, insert_params)
                update_params = {'category': category, 'link': item['link']}
                cursor.execute(self._UPDATE_SQL, update_params)
                conn.commit()

    # 更新时间，一次性
    @_db_pool.db_transaction
    def update_time(self, file_name, **kwargs):
        with open(file_name, 'r', encoding='utf8') as f:
            load_data = json.load(f)
        conn = kwargs['connection']
        with conn.cursor() as cursor:
            for item in load_data:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                sql = "UPDATE spider_book_data.book_info SET `create_time`=%s WHERE `title`=%s"
                params = (current_time, item['title'])
                cursor.execute(sql, params)
                conn.commit()

    # 更新标题，一次性
    @_db_pool.db_transaction
    def update_title(self, **kwargs):
        with open('book_philosophy', 'r', encoding='utf8') as f:
            load_data = json.load(f)
        conn = kwargs['connection']
        with conn.cursor() as cursor:
            for item in load_data:
                update_params = {'title': item['title'], 'link': item['link']}
                cursor.execute(self._UPDATE_TITLE_SQL, update_params)
                conn.commit()

    # 获取记录，测试
    @_db_pool.db_transaction
    def get_item(self, **kwargs):
        conn = kwargs['connection']
        with conn.cursor() as cursor:
            cursor.execute("select link from spider_book_data.book_info where book_info.pub_date NOT REGEXP '[0-9]{4}'")
            query = cursor.fetchall()
            wrong_list = [item[0] for item in query]
            return wrong_list


def baidu_translate(text):
    base_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    app_id = 20201207000640614
    app_secret = 'oD6n8nZ2tFxxs91bW0cl'
    salt = str(round(time.time() * 1000))
    sign_raw = str(app_id) + text + salt + app_secret
    sign = hashlib.md5(sign_raw.encode('utf8')).hexdigest()
    params = {
        'q': text,
        'from': 'auto',
        'to': 'en',
        'appid': app_id,
        'salt': salt,
        'sign': sign
    }
    response = requests.get(base_url, params=params).text
    json_data = json.loads(response)
    print(json_data)
    try:
        trans_res = [item['dst'].lower() for item in json_data['trans_result']]
        return ', '.join(trans_res)
    except Exception as e:
        logging.error(e)
        return "error"


def time_delay(func):
    @wraps(func)  # 保留原有函数名
    def wrapper_func(*args):
        result = func(*args)
        name = func.__name__
        if name == 'get_page' or 'get_book_info':
            time.sleep(random.randint(3, 10))
        elif name == 'get_url' or 'login':
            time.sleep(random.randint(3, 4))
        return result

    return wrapper_func
