import json
import pymysql
import time
import hashlib
import requests


# 将Json数据导入MYSQL中
def json_to_sql():
    with open('page_data', 'r', encoding='utf8') as f:
        load_data = json.load(f)
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='8281',
                               db='spider_book_data',
                               charset='utf8mb4')
        try:
            with conn.cursor() as cursor:
                for item in load_data:
                    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    sql = "INSERT INTO spider_book_data.psychology_book_data(`title`,`link`,`rate`,`evaluators`,`author`," \
                          "`press`,`pub_date`,`tags`,`comments`,`review`,`create_time`) " \
                          "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    params = (
                        item['title'], item['link'], item['rate'], item['evaluators'], item['author'], item['press'],
                        item['pub_date'], item['tags'], item['comments'], item['review'], current_time)
                    cursor.execute(sql, params)
                    conn.commit()
        except Exception:
            print("发生异常：" + str(Exception))
            conn.rollback()
        cursor.close()
        conn.close()


# 更新时间
def update_time():
    with open('page_data', 'r', encoding='utf8') as f:
        load_data = json.load(f)
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='8281',
                               db='spider_book_data',
                               charset='utf8mb4')
        try:
            with conn.cursor() as cursor:
                for item in load_data:
                    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    sql = "UPDATE spider_book_data.psychology_book_data SET `create_time`=%s WHERE `title`=%s"
                    params = (current_time, item['title'])
                    cursor.execute(sql, params)
                    conn.commit()
        except Exception:
            print("发生异常：" + str(Exception))
            conn.rollback()
        cursor.close()
        conn.close()


def baidu_translate(text):
    base_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    app_id = 20201207000640614
    app_secret = 'EQzCjSbEmZnYUoy4bRbn'
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
    trans_res = [item['dst'].lower() for item in json_data['trans_result']]
    return ','.join(trans_res)
