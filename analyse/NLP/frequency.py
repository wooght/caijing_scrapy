# -*- coding: utf-8 -*-
#
# @method   : 语料库数据结构
# @return   : freq->单词概率
# @Time     : 2017/11/27
# @Author   : wooght
# @File     : frequency.py

class freq(object):

    def exists(self, key):
        return hasattr(self, key)

    def get_rate(self, key):
        if not self.exists(key):
            return 1
        return self.__dict__[key]

    def freq(self, key):
        rate = self.get_rate(key)
        return float(rate) / self.total, rate

    def zero_freq(self):
        return 1 / self.total, 1

# a = {'a':1,'b':2,'c':3,'total':6}
# b = freq()
# b.__dict__ = a
# print(b.freq('b'))
# print(b.freq('e'))
