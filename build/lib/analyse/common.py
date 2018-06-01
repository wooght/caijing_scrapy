# -*- coding: utf-8 -*-
#
# @method   : 公共方法
# @Time     : 2017/12/27
# @Author   : wooght
# @File     : common.py

from .NLP.participle import pp
from .NLP.semantics import seman


# 获取关键词:上市公司,上市板块
def get_index(charts):
    listed_plate = {}
    listed_company = {}
    for x in pp.tags(charts):
        # x[0] 为pair对象: 单词/词性   x[1]为:权重
        # x[0].word 为单词 x[0].flag为词性
        if x[0].flag == 'nts':
            listed_company[x[0].word] = '%.2f' % x[1]
        if x[0].flag == 'ntp':
            listed_plate[x[0].word] = '%.2f' % x[1]
    return listed_plate, listed_company


def load_file(attitude_file):
    seman.load(attitude_file)


# 获取所在句子的语义情感打分
def get_lists(charts, ju):
    totle = []
    for j in ju:
        if charts in j:
            if len(charts) * 3 > len(j):
                # 长度不够,视为无判断意义
                continue
            # s = SnowNLP(j)
            # totle.append(s.sentiments)
            totle.append(seman.attitude(j))  # 语义打分
    try:
        avg = sum(totle) / len(totle)
    except:
        avg = 0.1  # 返回0.1 与没有的区分开
    return '%.2f' % avg


# 获取单个句子/一段话的态度
def get_one(ju):
    return seman.attitude(ju)
