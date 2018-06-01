# -*- coding: utf-8 -*-
#
# @method   : 大单/主力仓库
# @Time     : 2018/1/20
# @Author   : wooght
# @File     : ddtj.py

from ..Db import *

select_volumns = [ddtj.c.totalamt, ddtj.c.totalamtpct, ddtj.c.totalvol, ddtj.c.totalvolpct,
                  ddtj.c.stockvol, ddtj.c.stockamt, ddtj.c.opendate, ddtj.c.kuvolume,
                  ddtj.c.kdvolume, ddtj.c.code_id]


def one(code_id):
    s = select(select_volumns).where(ddtj.c.code_id == code_id)
    r = conn.execute(s)
    return r.fetchall()


def all():
    s = select(select_volumns)
    r = conn.execute(s)
    return r.fetchall()


def all_t(t):
    s = select(select_volumns).where(ddtj.c.opendate > t)
    r = conn.execute(s)
    return r.fetchall()
