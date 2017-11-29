# -*- coding: utf-8 -*-
#
# 转义分析 wooght
# by wooght
# 2017-11
#
import os
data_path = os.path.dirname(__file__)+"/corpus/change_words.txt"
class changehmm(object):
    def __init__(self):
        self.change_words = {'fty','ty','lty'}
        self.pos_words = {}
        self.neg_words = {}
        self.pass_num = 3
    def load(self,path):
        f = open(path,'r')
        for word in f.readlines():
            self.words.append(word)
        f.close()

    def hmm(self,words,key):
        tags = self.get_tags(words)
        for c in self.change_words:
            if(c in tags):
                num=0
                if(c=='fty' or c=='ty'):
                    while key>0 and num<self.pass_num:
                        key -=1
                        if(tags[key]==c):
                            return True
                        num+=1
                elif(c=='lty'):
                    while key<len(tags) and num<self.pass_num:
                        key+=1
                        if(tags[key]==c):
                            return True
                        num+=1
        return False

    def get_tags(self,words):
        tags = []
        for w in words:
            tags.append(w[1])
        return tags
