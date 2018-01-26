# -*- coding: utf-8 -*-
#
# @method   : 上市公司仓库
# @Time     : 2018/1/24
# @Author   : wooght
# @File     : companies.py

from ..Db import *


def all_codes():
    s = select([listed_company.c.codeid])
    r = conn.execute(s)
    return r.fetchall()


def all_codenames():
    s = select([listed_company.c.codeid, listed_company.c.name])
    r = conn.execute(s)
    return r.fetchall()
