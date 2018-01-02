# -*- coding: utf-8 -*-
#
# @method   : 加载txt文本中的单词,存放数据库中
# @Time     : 2017/12/29
# @Author   : wooght
# @File     : load_words.py

from model import T

txt_path = '../NLP/corpus/key_words.txt'


# 加载txt文档
def load(path):
    f = open(path, 'r', encoding='utf-8')
    words = []
    for i in f.readlines():
        dict = {}
        word = i.strip().split(' ')
        dict['word'] = word[0]
        if len(word) > 3:
            tmp = ''
            for w in word[:-2]:
                tmp += w
            dict['word'] = tmp
        dict['rate'] = word[-2]
        dict['nature'] = word[-1]
        words.append(dict)
    f.close()
    return words

# 保存数据库
def save_data():
    i = T.ch_dict.insert()
    list = load(txt_path)
    r = T.conn.execute(i, list)
    if r:
        print(r.rowcount)
    else:
        print('error')

# 添加新词到ch_dict
def add_dict():
    ch_s = T.select([T.ch_dict.c.word]).where(T.ch_dict.c.rate == '100000.00')
    ch_r = T.conn.execute(ch_s)
    ch_dict = []
    for i in ch_r.fetchall():
        ch_dict.append(i[0])
    print(ch_dict)
    cp_s = T.select([T.listed_company.c.name])
    cp_r = T.conn.execute(cp_s)
    new_dict = []
    for n in cp_r.fetchall():
        if n[0] not in ch_dict:
            tmp = {}
            tmp['word'] = n[0]
            tmp['rate'] = '100000'
            tmp['nature'] = 'nts'
            new_dict.append(tmp)
    i = T.ch_dict.insert()
    r = T.conn.execute(i,new_dict)
    if r.rowcount>0:
        print(r.rowcount, '新添加')

add_dict()