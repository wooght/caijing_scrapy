# -*- coding: utf-8 -*-
#
# @method   : 生产jieba keywords txt文件
# @Time     : 2017/12/29
# @Author   : wooght
# @File     : make_txt.py

from model import T

txt_path = '../NLP/corpus/key_words.txt'

# 生产txt文件
def make_keywords(txt_path):
    s = T.select([T.ch_dict.c.word, T.ch_dict.c.rate, T.ch_dict.c.nature])
    r = T.conn.execute(s)
    f = open(txt_path, 'w', encoding='utf-8')

    for i in r.fetchall():
        tmp = dict(i)
        f.write(i['word'] + ' ' + str(int(i['rate'])) + ' ' + i['nature'] + '\n')
    f.close()


make_keywords(txt_path)
