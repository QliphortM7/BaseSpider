import wordcloud
import imageio
import json
from matplotlib import pyplot as plt
from matplotlib import colors


# 绘制词云
def create_wordcloud():
    color_list = ['#9999FF', '#FF9966', '#99CC99', '#66CCCC', '#FF9900', '#999999', '#FF6666', '#669933', '#3399CC']
    colormap = colors.ListedColormap(color_list)
    pic = imageio.imread('material.png')
    img_color = wordcloud.ImageColorGenerator(pic)
    wc = wordcloud.WordCloud(mask=pic, width=800, height=1000, background_color='white',
                             max_words=150, font_path='msyh.ttc', colormap=colormap,
                             stopwords={'心理', '心理學', '好书', '值得一读', '我想读这本书', '樊登读书会', '入门'})
    tags = ""
    with open('page_data', 'r', encoding='utf8') as file:
        load_data = json.load(file)
        tags = load_data[0]['tags']
        for i in range(len(load_data)-1):
            tags = tags + "," + load_data[i+1]['tags']
    wc.generate(tags)
    # plt.imshow(wc)
    # plt.axis("off")
    # plt.show()
    wc.to_file('wc.png')  # 保存为图片
