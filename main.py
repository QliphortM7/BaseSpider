import time
import tools
import analysis
import selenium_spider

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start = time.time()
    spider = selenium_spider.SeleniumSpider('政治学')
    spider.execute_task()
    # l1 = spider.get_page('https://book.douban.com/tag/%E5%93%B2%E5%AD%A6?start=580&type=T')

    # analysis.create_wordcloud()
    end = time.time()
    print("运行时间：" + str(end - start))
