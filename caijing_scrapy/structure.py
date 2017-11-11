# -*- coding: utf-8 -*-
#
# 数据结构
# by wooght 2017-11
#

__author__ = 'wooght'
from sqlalchemy import create_engine, Table, Column ,MetaData, select
from sqlalchemy import VARCHAR as Varchar,TEXT as Text, Integer, String, ForeignKey
import re

engine = create_engine("mysql+pymysql://root:wooght565758@localhost:3306/scrapy?charset=utf8",encoding="utf-8", echo=True)
metadata = MetaData()

#上市公司表
listed_company = Table('listed_company',metadata,
    Column('id',Integer,primary_key=True),
    Column('father_id',Integer),            #总公司ID
    Column('code',Integer,index=True),      #股票代码
    Column('name',String(32)),              #公司名称
    Column('url',String(128)),              #公司官网
    Column('blog_url',String(128))          #官方微博
)


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

# 上市公司:Listed company
# ID
# 总公司ID		father_id
# 股票代码		code
# 所属板块		plate_id
# 公司名称		name
# 官网		url
# 微博		blog
#
# 公司-公司关系:cp_relation
# ID
# 公司1ID		cp_id
# 公司2ID		cp2_id
# 关系		level
# 		持股		1
#
#
# 板块分类:shares_plate
# ID
# 父板块ID		father_id
# 名称		name
#
#
# 重要人物:character
# ID
# 名称		name
# 微博		blog
#
# 公司-人物关系:cc_relation
# ID
# 公司ID		company_id
# 人物ID		character_id
# 人物级别		level
# 		法人		1
# 		股东/懂事	2
# 		经理/管理	3
# 		投资商		4
# 		持股		5
# 		家属		6
# 		员工		7
#
# 微博:blog
# ID
# 发布作者		author_id
# 作者类型		author_level
# 		1公司
# 		2人物
# 发布时间		pubdate
# 发布内容		body
# 分词		participle
# 关键词		word_key
