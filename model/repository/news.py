# -*- coding: utf-8 -*-
#
# @method   : 新闻表仓库
# @Time     : 2018/3/27
# @Author   : wooght
# @File     : news.py

from ..Db import *


def all():
    s = select([news.c.body, news.c.id])
    r = conn.execute(s)
    return r.fetchall()

def all_url():
    s = select([news.c.url])
    r = conn.execute(s)
    return r.fetchall()
