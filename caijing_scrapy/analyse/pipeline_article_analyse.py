#encoding utf-8
#
# scrapy pipeline 调用此
# 对body进行snownpl分析
# by Wooght
# 2017-11
#

import sys,io
# from ..settings import BOT_PATH
dir = __file__.split('\\');del dir[-2:];path = '/'.join(dir);sys.path.append(path)
from model import topic
from analyse.NLP.participle import pp
from analyse.NLP.semantics import seman
import re
from snownlp import SnowNLP
from snownlp import sentiment

class article_analyse():
    #分词,获取关键词
    #return 关键词,权重
    def get_index(self,str):
        listed_plate = {}
        listed_company = {}
        # 自定义词性 nts 股票公司名称,ntp 板块分类名称
        for x in pp.tags(str):
            # x[0] 为pair对象: 单词/词性   x[1]为:权重
            # x[0].word 为单词 x[0].flag为词性
            if(x[0].flag=='nts'):
                listed_company[x[0].word] = '%.2f'%x[1]
            if(x[0].flag=='ntp'):
                listed_plate[x[0].word] = '%.2f'%x[1]
        return listed_plate,listed_company

    #获取语义平均值
    def get_sentiments(self,str,ju):
        totle = []
        for j in ju:
            if(str in j):
                if(len(str)*3>len(j)):
                    #长度不够,视为无判断意义
                    continue
                # s = SnowNLP(j)
                # totle.append(s.sentiments)
                totle.append(seman.attitude(j))         #语义打分
                print(j,'\t',totle[-1])
        try:
            avg = sum(totle)/len(totle)
        except:
            avg = 0.1                       #返回0.1 与没有的区分开
        return '%.2f'%avg

    #分析接口
    # x.run(TopicItem)
    def run(self,item):
        listed_plate,listed_company = self.get_index(item['body'])
        article_ju = pp.cut_ju(item['body'])
        sql = {}
        if(len(listed_plate)>0):
            the_plate = max(listed_plate.items(),key=lambda d:d[1])     #只计算权重最大的一个
            the_sentiments = self.get_sentiments(the_plate[0],article_ju)    #态度打分
            item['plate_id'] = topic.s_plate_id(the_plate[0])           #生产sql修改语句字典
            item['plate_attitude'] = the_sentiments
        else:
            item['plate_id'] = 0    #没有则设置为0
        if(len(listed_company)>0):
            the_company = max(listed_company.items(),key=lambda d:d[1])
            the_sentiments = self.get_sentiments(the_company[0],article_ju)
            item['code_id'] = topic.s_company_id(the_company[0])
            item['cp_attitude'] = the_sentiments
        else:
            item['code_id'] = 0     #没有则设置为0

        return item
#调用方法
if(__name__=='__main__'):
    import sys,io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
    a = article_analyse()
    item={'body':'中国平安保险,哈哈哈哈,不错哦。保险行业也不错哦,回撤下行压力，现在发展势头比较好。但是中国平安会大涨还是大跌呢,下跌还是上涨呢,跌停还是涨停,是新高还是新低，这个还有看了行情反应才知道,我预计大跌眼镜。'}
    new_item = a.run(item)
    print(new_item)

# #计算关键词词频
# def str_freq(seg,indexwords):
#     word_freq = {}
#     for word in indexwords:
#         if word not in word_freq:
#             word_freq[word]=0
#         for w in seg:
#             if(word==w):
#                 word_freq[word]+=1
#     #sorted排序用法
#     return sorted(word_freq.items(),key=lambda d:d[1],reverse=True)      #reverse True降序, False默认升序 ,key 指对元素的某一部分进行排序
#
# fenci = jieba.lcut(body_str)
# word_freq = str_freq(fenci,indexwords)
# num=0
# for i,n in word_freq:
#     num+=1
#     print(i+'-','\t\t',n)
