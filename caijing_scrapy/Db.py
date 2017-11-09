# -*- coding: utf-8 -*-
__author__ = 'wooght'
from sqlalchemy import create_engine, Table, Column ,MetaData, select
from sqlalchemy import VARCHAR as Varchar,TEXT as Text, Integer, String, ForeignKey
import re

engine = create_engine("mysql+pymysql://root:wooght565758@localhost:3306/scrapy?charset=utf8",encoding="utf-8", echo=True)
metadata = MetaData()

#新闻表
news = Table('news',metadata,
    Column('id',Integer,primary_key=True),
    Column('url',Integer,nullable=False),       #网页地址ID号
    Column('only_id',String(32)),               #唯一标识,去重
    Column('title',String(128),nullable=True),  #新闻标题
    Column('body',Text),                        #新闻内容
    Column('put_time',String(64))               #发布时间
)
#话题表-分析文章
topic = Table('topic',metadata,
    Column('id',Integer,primary_key=True),
    Column('url',Integer,nullable=False),       #网页地址ID号
    Column('only_id',String(32)),               #唯一标识,去重
    Column('title',String(128),nullable=True),  #新闻标题
    Column('body',Text),                        #新闻内容
    Column('put_time',String(64))               #发布时间
)


metadata.create_all(engine)
conn = engine.connect()

import sys,io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
s = select([news.c.body,news.c.id]).where(news.c.id==7604)
r = conn.execute(s)
item = r.fetchone()
str = "<a href='www.baidu.com'>哈哈</a>"
re_str = re.sub(r'<[^<]*>','',item[0].strip())
print(re_str)

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

'''数据库设计'''
# 来源网站:
# ID
# URL
# TITLE
# 新闻类:

# ID
# URL           地址
# ONLY_id       唯一标识
# TITLE         标题
# BODY          内容
# CONTENT       内容,去HTML
# PUT_TIME      发布时间
# PUT_TIME_NUM  发布时间 时间暨
# SAVE_TIME     爬取时间
# FROM          来源
