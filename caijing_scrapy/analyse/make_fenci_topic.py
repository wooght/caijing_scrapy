#encoding utf-8
#
# 文章对象筛选
# 文章对象板块筛选
# 计算文章语义
# by Wooght
# 2017-11
#

import sys,io
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
from model import topic
import jieba
import jieba.posseg
import jieba.analyse
from snownlp import SnowNLP


#股票词典
jieba.load_userdict("F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy\analyse\words\key_words.txt")
#停用词
jieba.analyse.set_stop_words("F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy\analyse\words\stop_words.txt")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码


#分词,获取关键词
def get_index(str):
    listed_plate = {}
    listed_company = {}
    # 自定义词性 nts 股票公司名称,ntp 板块分类名称
    for x in jieba.analyse.extract_tags(str,withWeight=True,withFlag=True,allowPOS=('n','nt','nts','ntp','v','a','i','d','y','nian')):
        # x[0] 为pair对象: 单词/词性   x[1]为:权重
        # x[0].word 为单词 x[0].flag为词性
        if(x[0].flag=='nts'):
            listed_company[x[0].word] = '%.2f'%x[1]
        if(x[0].flag=='ntp'):
            listed_plate[x[0].word] = '%.2f'%x[1]
    return listed_plate,listed_company

#生产句子列表
def get_ju(body_str):
    if('。' in body_str):
        ju = body_str.split('。')
    elif('，' in body_str):
        ju = body_str.split('，')
    elif(',' in body_str):
        ju = body_str.split(',')
    else:
        ju = list(body_str)
    #解析句中句
    for j in ju:
        if('？' in j):
            i = ju.index(j)
            del ju[i]
            wj = j.split('？')
            ju = ju+wj
        elif('?' in j):
            i = ju.index(j)
            del ju[i]
            wj = j.split('?')
            ju = ju+wj
    return ju

#获取语义平均值
def get_sentiments(str,ju):
    totle = []
    for j in ju:
        if(str in j):
            s = SnowNLP(j)
            totle.append(s.sentiments)         #语义打分
            print(str,totle[-1])
    try:
        avg = sum(totle)/len(totle)
    except:
        avg = 0.00
    return '%.2f'%avg

#开始执行,执行数据库修改
def run(body_str,article_id):
    listed_plate,listed_company = get_index(body_str)
    article_ju = get_ju(body_str)
    sql = {}
    if(len(listed_plate)>0):
        the_plate = max(listed_plate.items(),key=lambda d:d[1])     #只计算权重最大的一个
        the_sentiments = get_sentiments(the_plate[0],article_ju)    #态度打分
        sql['plate_id'] = topic.s_plate_id(the_plate[0])            #生产sql修改语句字典
        sql['plate_attitude'] = the_sentiments
    else:
        sql['plate_id'] = 0    #没有则设置为0
    if(len(listed_company)>0):
        the_company = max(listed_company.items(),key=lambda d:d[1])
        the_sentiments = get_sentiments(the_company[0],article_ju)
        sql['code_id'] = topic.s_company_id(the_company[0])
        sql['cp_attitude'] = the_sentiments
    else:
        sql['code_id'] = 0     #没有则设置为0
    print(sql)
    if(len(sql)>1):
        up = topic.up(article_id,sql)

#运行入口
all_articles = topic.all()
for item in all_articles:
    run(item[0],item[1])

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
