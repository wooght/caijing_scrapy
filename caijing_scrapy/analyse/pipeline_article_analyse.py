#encoding utf-8
#
# scrapy pipeline 调用此
# 对body进行snownpl分析
# by Wooght
# 2017-11
#

import sys

# from ..settings import BOT_PATH
dir = __file__.split('/');del dir[-2:];path = '/'.join(dir);sys.path.append(path)

from model.repository import topic
from analyse.NLP.participle import pp
from analyse.NLP.semantics import seman


# from snownlp import SnowNLP
# from snownlp import sentiment

class article_analyse():
    #分词,获取关键词
    #return 关键词,权重
    def get_index(self,str):
        listed_plate = {}
        listed_company = {}
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
                # print(j,'\t',totle[-1])
        try:
            avg = sum(totle)/len(totle)
        except:
            avg = 0.1                       #返回0.1 与没有的区分开
        return '%.2f'%avg

    #分析接口
    # x.run(TopicItem)
    def run(self,item):
        result_item = []
        listed_plate,listed_company = self.get_index(item['body'])
        title_plate,title_company = self.get_index(item['title'])
        title_attitude = False
        if(len(title_company)>0):
            title_sentiments = seman.attitude(item['title'])
            print('title_sentiments:',title_sentiments)
            title_words = list(title_company)[0]
            title_attitude = True
        article_ju = pp.cut_ju(item['body'])
        if(len(listed_plate)>0):
            # the_plate = max(listed_plate.items(),key=lambda d:d[1])     #只计算权重最大的一个
            for plate in listed_plate.items():
                one_item={}
                the_sentiments = self.get_sentiments(plate[0],article_ju)    #态度打分
                one_item['plate_id'] = topic.s_plate_id(plate[0])           #生产sql修改语句字典
                one_item['plate_attitude'] = the_sentiments
                one_item['article_id'] = item['article_id']
                one_item['article_type'] = item['article_type']
                one_item['put_time'] = item['put_time']

                one_item['code_id'] = None
                one_item['cp_attitude'] = None
                result_item.append(one_item)
        if(len(listed_company)>0):
            # the_company = max(listed_company.items(),key=lambda d:d[1])
            for company in listed_company.items():
                one_item = {}
                the_sentiments = self.get_sentiments(company[0],article_ju)
                if(title_attitude and company[0]==title_words):
                    the_sentiments = float(the_sentiments)*0.4+float(title_sentiments)*0.6    #如果与表填相关,则标题占比提高
                one_item['code_id'] = topic.s_company_id(company[0])
                one_item['cp_attitude'] = the_sentiments
                one_item['article_id'] = item['article_id']
                one_item['article_type'] = item['article_type']
                one_item['put_time'] = item['put_time']

                one_item['plate_id'] = None
                one_item['plate_attitude'] = None
                result_item.append(one_item)

        return result_item
#调用方法
if(__name__=='__main__'):
    import sys,io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gbk') #改变标准输出的默认编码
    a = article_analyse()
    item={'title':'鸿路钢构签订涡阳县绿色装配式建筑产业园项目','article_id':1,'article_type':1,'put_time':123,
        'body':'中国证券网讯 鸿路钢构12月5日晚间披露，近日公司与涡阳县人民政府签订了《绿色装配式建筑产业园项目投资合作协议书》及《补充协议》，拟投资20亿元建设绿色装配式建筑产业园项目。　　产业园区主要项目包括：焊丝项目；薄壁轻钢别墅项目；立体车库项目；装配式建筑、钢结构及开平剪切配送项目；钢筋桁架楼层板、节能板及新型建材项目；机器人集成项目；重机项目；物流运输与装配式建筑设计院项目。项目用地位于涡阳县经开区绿色建筑产业集聚区内，用地面积约1000亩，建筑面积约40万平方米。　　公司称，本协议的签订是继2016年7月15日与涡阳人民政府签订《绿色生态建筑产业项目》战略合作协议后再次在沱牌舍得涡阳扩大投资，是双方对前一次合作的肯定，建成后将成为公司重要的装配式建筑产业基地，为公司装配式建筑业务的发展提供重要保障。如该项目顺利实施，未来几年公司将获得涡阳人民政府一定金额产业扶持奖励，有利于提升公司未来经营业绩。（胡心宇）'}
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
