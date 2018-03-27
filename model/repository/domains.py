# -*- coding: utf-8 -*-
#
# @method   : 域名仓库
# @Time     : 2018/3/27
# @Author   : wooght
# @File     : domains.py

from ..Db import *


def all():
    s = select([domains.c.name])
    r = conn.execute(s)
    return r.fetchall()
