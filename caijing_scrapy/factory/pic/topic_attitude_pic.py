#encoding utf-8
#
# topic语义分析图
# company_attitude
# Plate_Attitude
# by wooght
# 2017-11
#
import sys
sys.path.append('F:\homestead\scripy_wooght\caijing_scrapy\caijing_scrapy')
from basepic import Basepic
import model.Db as T
import providers.wfunc as wfunc
import json
import time
#获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 601318

#查询plate_id
ps = T.select([T.listed_company.c.plate_id]).where(T.listed_company.c.codeid==code_id)
pr = T.conn.execute(ps)
plate_id = pr.fetchall()[0][0]

class topic_attitude_pic(Basepic):

    def __init__(self,code_id,plate_id,*args,**kwargs):
        super(topic_attitude_pic,self).__init__(*args,**kwargs)
        self.code_id = code_id
        self.plate_id = plate_id
        #图片路径及名称
        self.now_day = wfunc.today(strtime=False)
        pic_name = self.pic_path+"\pic_attitude_topic\codes_"+str(code_id)+'_'+self.now_day
        self.pic_path = pic_name+".png"
        self.strip_pic_path = pic_name+"strip.png"
        #查询开始时间
        self.start = int(time.time()-90*3600*24)

    #attitude数据组装施工
    def select_atd(self,*args,**kargs):
        result = T.conn.execute(args[0])
        new_list = []
        for item in result.fetchall():
            obj = {};n=1
            put_time = time.strftime("%Y-%m-%d",time.localtime(int(item[0])))
            obj['time'] = put_time
            for i in kargs['columns']:
                # if(item[n]<0.5):
                #     obj[i] = (item[n]-1)*2
                # else:
                obj[i] = item[n]
                n+=1
            new_list.append(obj)
        new_pd = self.pd.DataFrame(data=new_list)
        #查询为空 返回模拟数据
        if(len(new_pd)<1):
            new_pd['time'] = self.pd.Series([1,2,3,4,5])
            for item in kargs['columns']:
                new_pd[item] = 0.01
            return new_pd
        new_pd['time'] = self.pd.to_datetime(new_pd['time'])
        for item in kargs['columns']:
            new_pd[item] = self.pd.to_numeric(new_pd[item])
        return new_pd

    #company_attitude 数据组装车间
    def select_cp_atd(self):
        #文章cp_attitude查询
        s = T.select([T.topic.c.put_time,T.topic.c.cp_attitude]).where(T.topic.c.code_id==self.code_id).where(T.topic.c.put_time>self.start)
        pddata = self.select_atd(s,columns = ['cp_attitude'])
        return pddata

    #plate_attitude 数据组装车间
    def select_plate_atd(self):
        #文章plate_attitude查询
        s = T.select([T.topic.c.put_time,T.topic.c.plate_attitude]).where(T.topic.c.plate_id==self.plate_id).where(T.topic.c.put_time>self.start)
        try:
            pddata = self.select_atd(s,columns = ['plate_attitude'])
        except:
            print(self.plate_id)
        return pddata

    #数据分组求平均
    def atd_mean(self,pandas,attitude,time):
        #分组
        attitudes = pandas.groupby('time',as_index=False)[attitude].agg({attitude:'mean'})
        return attitudes

    #分析数据组装
    def last_pandas(self,quotes,cp_atd,plate_atd):
        quotes.insert(1,'time',self.pd.to_datetime(quotes['datatime']))
        cp_atd = self.atd_mean(cp_atd,'cp_attitude','time')
        plate_atd = self.atd_mean(plate_atd,'plate_attitude','time')
        #合并
        quotes = self.pd.merge(quotes,cp_atd,on=['time'],how='left')
        quotes = self.pd.merge(quotes,plate_atd,on=['time'],how='left')
        quotes.index = quotes['time']
        #划定0.5语义中性线
        quotes.loc[:,'zero'] = 0.6
        return quotes
    #数据生成工厂
    def buide_datas(self):
        cp_atd = self.select_cp_atd()
        plate_atd = self.select_plate_atd()
        quotes = self.select_quotes(self.code_id)
        last_pandas = self.last_pandas(quotes,cp_atd,plate_atd)
        return last_pandas,cp_atd
    #运行接口
    def run(self):
        df,df2 = self.buide_datas()
        df = df.sort_values(by='time',ascending=True)
        self.sns.set(style="ticks",palette="muted",color_codes=True)
        self.plt.xlabel('datatime')
        self.plt.ylabel('shou')
        self.plt.title('Topic Attitude',fontsize=16,color='red')
        self.plt.grid(True)                  #是否显示网格
        #绘制 情感平均图/涨跌幅对比图
        self.plt.plot(df.loc[:,['zd_range','cp_attitude','zero']])
        self.plt.savefig(self.pic_path)
        self.plt.show()
        #绘制 情感分布散点图
        df2.index = self.pd.to_datetime(df2['time'])
        ax = self.sns.stripplot(x="time", y="cp_attitude", data=df2)
        ax.tick_params(axis='x',labelsize=4)
        self.plt.show()
        #绘制行业情感平均图
        # self.plt.title('Topic Plate_Attitude',fontsize=16,color='red')
        # self.plt.plot(df.loc[:,['zd_range','plate_attitude','zero']])
        df.drop(df[df['cp_attitude'].isnull()].index,inplace=True)
        self.sns.jointplot(x='zd_range',y='cp_attitude',data=df,kind="reg")
        self.plt.savefig(self.strip_pic_path)
        self.plt.show()
        print(self.now_day)

this = topic_attitude_pic(code_id,plate_id)
this.run()
