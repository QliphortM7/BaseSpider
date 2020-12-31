import time
import tools
import analysis
import selenium_spider

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start = time.time()
    # spider = selenium_spider.SeleniumSpider('哲学')
    # spider.execute_task()
    # l1 = spider.get_page('https://book.douban.com/tag/%E5%93%B2%E5%AD%A6?start=580&type=T')
    conn = tools.DBOperation()
    conn.update_title()

    # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # single_data = {'title': 'theme', 'link': 'https://book.douban.com/tag/%E5%BF%83%E7%90%86%E5%AD%A6?start=0&type=T',
    #              'rate':'7', 'evaluators': '1219', 'author': 'Job', 'press': 'null', 'pub_date': '1994',
    #              'tags': 'null', 'comments': '13', 'review': '4','create_time': current_time}
    # page_data = [single_data]
    # spider.save_mysql(page_data)
    # analysis.create_wordcloud()
    end = time.time()
    print("运行时间：" + str(end - start))
