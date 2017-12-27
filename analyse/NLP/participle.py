# -*- coding: utf-8 -*-
#
# @method   : 分词,分句
# @return   : words,ju
# @Time     : 2017/11/27
# @Author   : wooght
# @File     : participle.py
import os
import re

import jieba
import jieba.analyse
import jieba.posseg

data_path = os.path.dirname(__file__) + "/corpus/"
jieba.load_userdict(data_path + "key_words.txt")
stop_path = data_path + 'stopwords.txt'
jieba.analyse.set_stop_words(stop_path)


class pp(object):
    def __init__(self):
        self.seg = jieba.posseg
        self.stop_words = []

    def load(self, fname):
        f = open(fname, 'r', encoding='utf-8')
        words = f.readlines()
        for l in words:
            self.stop_words.append(l.strip())
        f.close()

    # 分句
    def cut_ju(self, str):
        ju_re = re.compile('[。？?]')
        ju = ju_re.split(str)
        return ju

    def lcut(self, str):
        cutstr = jieba.lcut(str)
        words = []
        for word in cutstr:
            if word not in self.stop_words:
                words.append(word)
        return words

    # 分词带词性
    def flag_cut(self, str, stop_flag=('x', 'ns')):
        cutstr = self.seg.lcut(str)
        words = []
        for word in cutstr:
            if word.word not in self.stop_words and word.flag not in stop_flag:
                words.append(word)
        return words

    # 关键词提取
    # 自定义词性 nts 股票公司名称,ntp 板块分类名称
    def tags(self, str, allpos=('nt', 'nts', 'ntp')):
        return jieba.analyse.extract_tags(str, withWeight=True, withFlag=True, allowPOS=allpos)


pp = pp()
pp.load(stop_path)  # 加载停用词

if __name__ == '__main__':
    import sys, io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
    s = "难道不利好,利好消息,虽然没有成功,是吗,难道,难道不是吗,不漂亮吗,莫非,真的,不涨吗,还不跌吗,没有价值吗,哪里来的上涨,怎能安心,增能由他上涨,怎能不涨,并没有上涨,没有像从前一样好了"
    word = pp.flag_cut(s)
    print(len(word))
    print(word)
