#encoding utf-8
#
# 生成分析图片基础模块
# by wooght
# 2017-11
#
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
import model.Db as T
from factory.basedata import basedata
import common.wfunc as wfunc
import matplotlib as mpl
import matplotlib.pyplot as plt     #matplotlib.pyplot 绘图主键
import seaborn as sns
import json

class Basepic(basedata):
    pic_path = 'F:\homestead\caijing_lvl\public'
    def __init__(self,*args,**kwargs):
        super(Basepic,self).__init__(*args,**kwargs)
        self.mpl = mpl
        self.plt = plt
        self.sns = sns
        self.plt.rcParams['font.sans-serif'] = ['SimHei']    #指定默认字体 解决中文问题
