#encoding utf-8
#
# 查询股票名称 写入jieba字典
# by wooght 2017-11
#

import sys,io
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
from model import Db as T
import jieba
import jieba.posseg
import jieba.analyse
import json

#查询上市公司名称 T.table_name.c['字段名称']  字段名称可以参数传递
def s_company(column_name):
    all_list = []
    s = T.select([T.listed_company.c[column_name]])
    r = T.conn.execute(s)
    for i in r.fetchall():
        all_list.append(i[0])
    return all_list;
#查询板块名称
def s_plate(column_name):
    all_list = []
    s = T.select([T.listed_plate.c[column_name]])
    r = T.conn.execute(s)
    for i in r.fetchall():
        all_list.append(i[0])
    return all_list;

r = s_plate('name')

# f = open('math_seaborn/words/key_words.txt','a+',encoding='utf-8')
# for i in r:
#     f.write(i+' '+'200000 ntp\n')
