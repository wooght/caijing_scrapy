# encoding utf-8
# ##################################
# topic attitude数据组转
# by wooght
# 2017-11
# ##################################
import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')
from factory.basedata import basedata
from model import T, rds
import time

# 获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 1000001


class attitude_data(basedata):
    def __init__(self, code_id, *args, **kwargs):
        super(attitude_data, self).__init__(*args, **kwargs)
        self.code_id = code_id
        # 查询开始时间
        self.start = int(time.time() - 720 * 3600 * 24)

    # company_attitude 数据组装车间
    def select_cp_atd(self, Tb, a_type):
        # 文章cp_attitude查询
        if str(self.code_id) == '1000001':
            where = Tb.c.code_id is not None
        else:
            where = Tb.c.code_id == self.code_id
        s = T.select([Tb.c.put_time, Tb.c.cp_attitude]).where(where).where(
            Tb.c.put_time > self.start).where(Tb.c.article_type == a_type)
        pddata = self.select_atd(s, columns=['cp_attitude'])
        return pddata

    # 分析数据组装
    def last_pandas(self, quotes, cp_atds, news_atds):
        quotes.insert(1, 'time', self.pd.to_datetime(quotes['datatime']))
        cp_atd = self.atd_mean(cp_atds, 'cp_attitude', 'time')
        news_atd = self.atd_mean(news_atds, 'cp_attitude', 'time')
        cp_count = self.atd_count(cp_atds, 'cp_attitude', 'time')
        cp_count['cp_count'] = cp_count['cp_attitude'];
        del cp_count['cp_attitude']
        news_count = self.atd_count(news_atds, 'cp_attitude', 'time')
        news_count['news_count'] = news_count['cp_attitude'];
        del news_count['cp_attitude']
        # 合并
        quotes = self.pd.merge(quotes, news_atd, on=['time'], how='left')
        quotes = self.pd.merge(quotes, cp_count, on=['time'], how='left')
        quotes = self.pd.merge(quotes, news_count, on=['time'], how='left')
        quotes = self.pd.merge(quotes, cp_atd, on=['time'], how='left').fillna(
            0)  # .fillna(cp_atd.cp_attitude.median())
        quotes.index = quotes['time']
        # 划定0.5语义中性线
        quotes.loc[:, 'zero'] = 0.6
        return quotes

    # 数据生成工厂
    def buide_datas(self):
        cp_atd = self.select_cp_atd(T.attitude_relation, 1)
        cp_news_atd = self.select_cp_atd(T.attitude_relation, 2)
        quotes = self.select_quotes(self.code_id)
        last_pandas = self.last_pandas(quotes, cp_atd, cp_news_atd)
        return last_pandas, cp_atd

    # web api
    def web_data(self, *args, **kwargs):
        result_arr = []
        for item in args[0].index:
            item_arr = []
            item_arr.append(args[0].loc[item, args[1]])
            for cols in kwargs['columns']:
                item_arr.append('%0.2f' % args[0].loc[item, cols])
            result_arr.append(item_arr)
        return result_arr

    # 运行接口
    def run(self):
        df, df2 = self.buide_datas()
        df = df.sort_values(by='time', ascending=True)
        a = self.web_data(df, 'datatime', columns=['shou', 'cp_attitude_y', 'cp_attitude_x', 'cp_count', 'news_count'])
        rds.hset('topic_attitude', self.code_id, a)
        print(a)


if __name__ == '__main__':
    if not rds.hexists('topic_attitude', code_id):
        a = attitude_data(code_id)
        a.run()
    else:
        a = rds.hget('topic_attitude', code_id).decode('utf-8')
        # rds.delete('topic_attitude')
        print(a)
