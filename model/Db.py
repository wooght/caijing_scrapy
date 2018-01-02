# -*- coding: utf-8 -*-
#
# 数据库操作 sqlalchemy
# by wooght 2017-11
#

__author__ = 'wooght'
from sqlalchemy import create_engine, Table, Column, MetaData, select
from sqlalchemy import VARCHAR, TEXT as Text, Integer, String, ForeignKey, Date, Float, SmallInteger, \
    BigInteger
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("mysql+pymysql://homestead:secret@192.168.10.10:3306/scrapy?charset=utf8", encoding="utf-8",
                       echo=False)  # echo表示是否输出执行过程内容
metadata = MetaData()

# 地域表
listed_region = Table('listed_region', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('father_id', Integer),  # 上级
                      Column('name', String(32))
                      )

# 上市公司表
listed_company = Table('listed_company', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('father_id', Integer),  # 总公司ID
                       Column('codeid', Integer, index=True),  # 股票代码
                       Column('region_id', Integer),  # 地区ID
                       Column('plate_id', Integer),  # 板块ID
                       Column('concept_id', String(255)),  # 概念板块
                       Column('name', String(32)),  # 公司名称
                       Column('url', String(128)),  # 公司官网
                       Column('blog_url', String(128)),  # 官方微博
                       Column('shsz', String(16))  # 沪深板块
                       )

# 行情表
quotes = Table('quotes', metadata,
               Column('id', Integer, primary_key=True),
               Column('datatime', Date),  # 日期
               Column('code_id', SmallInteger),  # 股票代码
               Column('gao', Float),  # 高
               Column('kai', Float),  # 开
               Column('di', Float),  # 底
               Column('shou', Float),  # 收
               Column('before', Float),  # 前收
               Column('zd_money', Float),  # 涨跌额
               Column('zd_range', Float)  # 涨跌幅
               )

# 行情一行表
quotes_item = Table('quotes_item', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('code_id', SmallInteger, index=True),  # 股票代码
                    Column('quotes', Text),  # 60天行情
                    Column('update_at', Date)  # 最后修改时间
                    )

# 公司公告
company_notice = Table('company_notice', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('datatime', Date),  # 日期
                       Column('code_id', SmallInteger),  # 股票代码
                       Column('title', String(128)),
                       Column('body', Text),
                       )

# 板块分类
listed_plate = Table('listed_plate', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('plateid', SmallInteger, index=True),  # 网易行业ID
                     Column('father_id', Integer),  # 父类ID
                     Column('name', String(32)),
                     )
# 概念板块
listed_concept = Table('listed_concept', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('conceptid', SmallInteger, index=True),  # 网易行业ID
                       Column('father_id', Integer),  # 父类ID
                       Column('name', String(32)),
                       )

# 新闻表
news = Table('news', metadata,
             Column('id', Integer, primary_key=True),
             Column('url', Integer, nullable=False),  # 网页地址ID号
             Column('only_id', String(32)),  # 唯一标识,去重
             Column('title', String(128), nullable=True),  # 新闻标题
             Column('body', Text),  # 新闻内容
             Column('put_time', String(64)),  # 发布时间
             Column('code_id', Integer),  # 公司codeid
             Column('cp_attitude', Float),  # 公司态度
             Column('plate_id', Integer),  # 板块plateid
             Column('plate_attitude', Float)  # 板块态度
             )
# 话题表-分析文章
topic = Table('topic', metadata,
              Column('id', Integer, primary_key=True),
              Column('url', String(128), nullable=False),
              Column('only_id', String(32)),  # 唯一标识,去重
              Column('title', String(128), nullable=True),  # 新闻标题
              Column('body', Text),  # 新闻内容
              Column('body_fenci', Text),  # 内容分词
              Column('key_words', String(255)),  # 关键词
              Column('put_time', String(64)),  # 发布时间
              Column('code_id', Integer),  # 公司codeid
              Column('cp_attitude', Float),  # 公司态度
              Column('plate_id', Integer),  # 板块plateid
              Column('plate_attitude', Float)  # 板块态度
              )

# 问答表-专家或机构回答
qanda = Table('qanda', metadata,
              Column('id', Integer, primary_key=True),
              Column('url', String(255), nullable=False),
              Column('only_id', String(32)),  # 唯一标识,去重
              Column('title', String(128)),  # 问答标题
              Column('body', Text),  # 问答内容
              Column('body_fenci', Text),  # 内容分词
              Column('key_words', String(255)),  # 关键词
              Column('put_time', String(64)),  # 发布时间
              Column('code_id', Integer),  # 公司codeid
              Column('cp_attitude', Float),  # 公司态度
              Column('plate_id', Integer),  # 板块plateid
              Column('plate_attitude', Float)  # 板块态度
              )
# 网址域
domains = Table('domains', metadata,
                Column('id', Integer, primary_key=True),
                Column('url', String(255), nullable=False),
                Column('name', String(32)),
                )
# 大单统计
ddtj = Table('ddtj', metadata,
             Column('id', Integer, primary_key=True),
             Column('code_id', Integer),
             Column('only_id', String(32)),  # 唯一标识
             Column('totalamt', Float),  # 成交额
             Column('totalamtpct', Float),  # 成交占比
             Column('totalvol', Float),  # 成交量
             Column('totalvolpct', Float),  # 成交量占比
             Column('stockvol', Float),  # 总成交量
             Column('stockamt', Float),  # 总成交额
             Column('kuvolume', Float),  # 主买量
             Column('kdvolume', Float),  # 主卖量
             Column('kuamount', Float),  # 主买额
             Column('kdamount', Float),  # 主卖额
             Column('avgprice', Float),  # 均价
             Column('opendate', Date),  # 日期
             )
# 语义打分关联表
attitude_relation = Table('attitude_relation', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('code_id', Integer, index=True),
                          Column('cp_attitude', Float),
                          Column('plate_id', Integer),
                          Column('plate_attitude', Float),
                          Column('article_id', Integer),
                          Column('article_type', SmallInteger),  # 文章分类,1位topic,2位news
                          Column('put_time', String(64)),
                          )
# 雪球组合
xq_zuhe = Table('xq_zuhe', metadata,
                Column('id', Integer, primary_key=True),
                Column('zh_symbol', String(16), index=True),  # 组合编号
                Column('zh_id', Integer),  # 组合ID
                Column('owner_id', BigInteger),  # 所属者ID
                Column('zh_name', String(64)),  # 组合名称
                )
# 组合调仓记录
zuhe_change = Table('zuhe_change', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('zh_symbol', String(16), index=True),  # 组合编号
                    Column('change_id', Integer),  # 调仓ID
                    Column('stock_name', String(32)),  # 股票名称
                    Column('code_id', Integer),  # 股票代码
                    Column('prev_weight', Float),  # 前值
                    Column('target_weight', Float),  # 后值
                    Column('change_status', Float),  # 变化
                    Column('updated_at', String(32)),  # 调整时间
                    )

# 词典
ch_dict = Table('ch_dict', metadata,
                Column('id', Integer, primary_key=True),
                Column('word', VARCHAR(32)),    # 实体
                Column('rate', Float(16, 2)),  # 词频
                Column('nature', VARCHAR(8)),   # 词性
                Column('sentiment', Float(16, 2))  # 情感
                )

metadata.create_all(engine)  # 创建所有表
conn = engine.connect()
#
# #删除html标签
# def delete_html(str):
#     re_str = re.sub(r'<[^>]*>','',str.strip())
#     return re_str
#
# def alldelete(topic):
#     s = select([topic.c.id,topic.c.body])
#     r = conn.execute(s)
#     num = 0
#     for i in r.fetchall():
#         new_body = delete_html(i[1])
#         u = topic.update().where(topic.c.id==i[0]).values(body=new_body)
#         result = conn.execute(u)
#         if(result.rowcount==1):
#             num+=1
#         else:
#             print('Error!--->行数为:',result.rowcount)
#
#         print(num,'修改成功!')
# alldelete(news)

# s = select([news.c.url,news.c.only_id,news.c.title,news.c.body,news.c.put_time]).where(news.c.put_time>10000000000)
# r = conn.execute(s)
# items = r.fetchall()
# new_arr = []
# for item in items:
#     new_arr.append({'url':item[0],'only_id':item[1],'title':item[2],'body':item[3],'put_time':item[4]})
#
# i = topic.insert()
# r = conn.execute(i,new_arr)
# if(r):
#     print(r.rowcount)

# i = sns_sseinfo.insert()
# list = dict(time='2017-10-10',ask='aa',anwser='11',dm='11')
# print(i)
# r = conn.execute(i,list)
