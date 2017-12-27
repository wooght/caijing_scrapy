# -*- coding: utf-8 -*-
#
# @method   : 前端语义分析展示数据组装
# @Time     : 2017/12/27
# @Author   : wooght
# @File     : semantics.py

from data_config import sys_path
import sys

sys.path.append(sys_path)
from model import topic
from analyse.common import *
from analyse.NLP.participle import pp
from analyse.NLP.semantics import seman

try:
    article_id = sys.argv[1]
except:
    article_id = 47512


class semantics:
    title = ''
    body = ''
    keywords = []
    words = []
    ju = []
    zf = []

    def __init__(self, article_id):
        articles_dict = dict(topic.one(article_id))
        self.title = articles_dict['title']
        self.body = articles_dict['body'].strip()
        keywords = pp.tags(self.body, allpos=('n', 'a', 'nt', 'v', 'd', 'ns'))
        for words in keywords:
            ws = [words[0].word.encode('utf-8'), words[0].flag, words[1]]
            self.keywords.append(ws)
        words = pp.flag_cut(self.body)
        for w in words:
            self.words.append([w.word.encode('utf-8'), w.flag])
        ju = pp.cut_ju(self.body)
        for j in ju:
            fen = seman.attitude(j)
            self.ju.append([j.strip().encode('utf-8'), fen])
        listed_plate, listed_company = get_index(self.body)
        if len(listed_company) > 0:
            for companys in listed_company.items():
                cfen = get_sentiments(companys[0], ju)
                self.zf.append([companys[0].encode('utf-8'), companys[1], cfen])


wrun = semantics(article_id)
return_dict = {
    'zf': wrun.zf,
    'body': wrun.body.encode('utf-8'),
    'title': wrun.title.encode('utf-8'),
    'ju': wrun.ju,
    'keywords': wrun.keywords,
    'words': wrun.words,
}
# print(sys.getdefaultencoding()) # 输出当前编码
print(return_dict)
