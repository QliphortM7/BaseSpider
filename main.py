import time
import spider

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start = time.time()
    url = 'https://book.douban.com/tag/%E5%BF%83%E7%90%86%E5%AD%A6?start=0&type=T'
    spider.get_url_data(url)
    end = time.time()
    print("运行时间：" + str(end - start))
