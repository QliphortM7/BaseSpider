import json
import pymysql
import time


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
