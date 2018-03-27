# -*- coding: utf-8 -*-
#
# @method   : 文章分类统计
# @Time     : 2018/3/27
# @Author   : wooght
# @File     : article_nums.py

import os
import sys
sys.path.append(os.path.dirname(__file__) + '/../../')
from model import news, topic, domains, rds


def run():
    articles_t = topic.all_url()
    articles_n = news.all_url()
    articles_domains = domains.all()
    ats_domains = []
    for i in articles_domains:
        ats_domains.append(i[0])
    topics_lists = {}
    news_lists = {}
    for i in articles_t:
        tmp = dict(i)['url']
        for n in ats_domains:
            if n+".com" in tmp:
                if n in topics_lists.keys():
                    topics_lists[n] += 1
                else:
                    topics_lists[n] = 1

    for i in articles_n:
        tmp = dict(i)['url']
        for n in ats_domains:
            if n+".com" in tmp:
                if n in news_lists.keys():
                    news_lists[n] += 1
                else:
                    news_lists[n] = 1

    rds.hmset('articles_nums', {'topics': topics_lists, 'news': news_lists})


if not rds.hexists('articles_nums', 'topics'):
    run()
result = rds.hmget('articles_nums', 'topics')[0].decode('utf8')
print("["+rds.hmget('articles_nums', 'topics')[0].decode('utf8'), ',', rds.hmget('articles_nums', 'news')[0].decode('utf8')+"]")
rds.delete('articles_nums')