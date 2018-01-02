# -*- coding: utf-8 -*-
#
# @method   : 修改company的名字,并将新词添加到ch_dict
# @Time     : 2017/12/29
# @Author   : wooght
# @File     : up_companies.py

from model import T
import re

# 去空,替换A,B
def update_ab(r):
    companies = []
    for cp in r.fetchall():
        s = cp[0]
        handalb = re.compile(r'Ｂ')
        handala = re.compile(r'Ａ')
        s = re.sub(handala, 'A', s)
        s = re.sub(handalb, 'B', s)
        s = re.sub(' ', '', s)
        companies.append((s, cp[1]))
    return companies

# 修改listed_company表
def thecompany():
    s = T.select([T.listed_company.c.name, T.listed_company.c.id])
    r = T.conn.execute(s)
    companies = update_ab(r)
    for cp in companies:
        u = T.listed_company.update().where(T.listed_company.c.id == cp[1]).values(name=cp[0])
        r = T.conn.execute(u)
        if r.rowcount == 1:
            print(cp[0], '修改成功...')

# 修改ch_dict表
def thechdict():
    s = T.select([T.ch_dict.c.word, T.ch_dict.c.id]).where(T.ch_dict.c.rate=='100000.00')
    r = T.conn.execute(s)
    new_dicts = update_ab(r)
    for cp in new_dicts:
        u = T.ch_dict.update().where(T.ch_dict.c.id == cp[1]).values(word=cp[0])
        r = T.conn.execute(u)
        if r.rowcount == 1:
            print(cp[0], '修改成功...')

thechdict()
