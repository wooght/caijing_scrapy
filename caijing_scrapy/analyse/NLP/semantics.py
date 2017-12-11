# -*- coding: utf-8 -*-
################################################
# 语义分析
# 朴素贝叶斯分类
# by wooght
# 2017-11
################################################
import os,sys
sys.path.append(os.path.dirname(__file__))
from participle import pp
from frequency import freq
from changeask import changehmm
import pickle
import marshal

from math import log,exp

data_path = os.path.dirname(__file__)+"/corpus/"

#朴素贝叶斯 模型
class NB(object):
    def __init__(self):
        self.words = {}
        self.ask = {}
        self.total = 0
        self.pass_words = {'x','m','url','nian','eng','nts','ntp','y','yue'}   #pass的词性
        self.passive_words = {'v','a'}                      #被动转义词性
        self.changehmm = changehmm()

    #加载序列化数据
    def load(self,path):
        f = open(path,'rb')
        arr = marshal.load(f)
        for i in arr:
            self.ask[i] = freq()
            self.ask[i].__dict__ = arr[i]
            self.total+=arr[i]['total']
        f.close()

    #加载语料库
    def load_corpus(self,pospath,negpath):
        map_list = [('pos',pospath),('neg',negpath)]
        for map in map_list:
            lines = []
            f = open(map[1],'r',encoding='utf-8')
            for l in f.readlines():
                lines.append(l.strip())
            f.close()
            self.pp_rate(map[0],lines)

    #简单分词,返回词性
    def pp(self,str):
        pp_words = pp.flag_cut(str)
        words = []
        for word in pp_words:
            if(word.flag not in self.pass_words):
                words.append((word.word,word.flag))
        return words

    #分词,返回词性,词频
    def pp_rate(self,map,lines):
        totle = 0
        dicts = {}
        for line in lines:
            words = pp.flag_cut(line)
            for word in words:
                if(word.flag not in self.pass_words):
                    if(word.word not in dicts):
                        dicts[word.word]=1
                    else:
                        dicts[word.word]+=1
                    totle+=1
        dicts['total'] = totle
        self.words[map] = dicts

    #序列化数据 保存训练好的语料库
    def save(self,path):
        f = open(path,'wb')
        marshal.dump(self.words,f)
        f.close()

    #贝叶斯分类器 返回分类及分类概率
    def classfaly(self, askwords):
        log_num = {}
        for i in self.ask:
            log_num[i] = log(self.ask[i].total) - log(self.total)               #组单词总量的对数差 <0
            key = 0
            for word in askwords:
                if(word[1] in self.passive_words):
                    if(self.changehmm.hmm(askwords,key)):
                        print('\t',i,word,self.ask[i].zero_freq())
                        log_num[i]+=log(self.ask[i].zero_freq()[0])
                        continue
                log_num[i] += log(self.ask[i].freq(word[0])[0])                    #所在组的频率对数 <<0
                key+=1
        ret, prob = '', 0
        for k in self.ask:
            exp_num = 0
            try:
                for otherk in self.ask:
                    exp_num += exp(log_num[otherk]-log_num[k])                  #exp_num = 1+对数差的幂 注意这里减数和被减数
                exp_num = 1/exp_num
            except OverflowError:
                exp_num = 0
            if exp_num > prob:
                ret, prob = k, exp_num                                          #返回概率大的概率和标识
        return (ret, prob)

    #态度分析
    def attitude(self,str):
        words = self.pp(str)
        ret,prob = self.classfaly(words)
        if(ret=='neg'):
            return 1-prob                                                        #负面态度 设定为负数
        return prob


seman = NB()
seman.load(data_path+"semantics.wooght")

if(__name__=='__main__'):
    import sys,io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
    seman.load_corpus(data_path+"positive.txt",data_path+"negative.txt")
    seman.save(data_path+"semantics.wooght")
    # 调用方法
    print(seman.attitude('以创业板公司翰宇药业为例，该公司四季度以来分5次共接受了45家基金的组团调研，在所有公司中接受基金调研的次数和家数居首'))
