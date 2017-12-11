#encoding utf-8
#
# 爬虫统计分析图
# by wooght
# 2017-11
#
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
import model.Db as T
import providers.wfunc as wfunc
from basepic import Basepic
import time
import json

class total_classfaly_pic(Basepic):
    def __init__(self,*args,**kwargs):
        super(total_classfaly_pic,self).__init__(*args,**kwargs)
        self.path_news = self.pic_path+'/total_classfaly_pic/news_total.png'
        self.path_topic = self.pic_path+'/total_classfaly_pic/topic_total.png'
    #查询domains
    def select_domains(self):
        s = T.select([T.domains.c.name])
        r = T.conn.execute(s)
        arr = []
        for i in r:
            arr.append(i[0])
        return arr

    #查询文章
    def select_article(self,Table):
        s = T.select([Table.c.url])
        r = T.conn.execute(s)
        arr = []
        for i in r:
            arr.append(i[0])
        return arr
    #数量计算
    def math_count(self,urls,domains):
        count_arr = self.pd.Series(self.np.zeros(len(domains)),index=domains)
        for url in urls:
            for d in domains:
                if(d in url):
                    count_arr[d]+=1
                    break
        return count_arr

    #数据组装
    #plt图片展示
    def show(self,Table):
        domains = self.select_domains()
        urls = self.select_article(Table)
        count_arr = self.math_count(urls,domains)
        pd_arr = self.pd.DataFrame(count_arr)
        pd_arr.drop(pd_arr[pd_arr[0]==0].index,inplace=True) #inplace 指在原结构上操作
        self.sns.barplot(y=pd_arr.index,x=pd_arr[0])
        self.plt.xlabel('统计分布',fontsize=16)
    def save_pic(self,path):
        print(path)
        self.plt.savefig(path)
        self.plt.show()
    def run(self):
        self.show(T.news)
        self.save_pic(self.path_news)
        self.show(T.topic)
        self.save_pic(self.path_topic)

a = total_classfaly_pic()
a.run()
