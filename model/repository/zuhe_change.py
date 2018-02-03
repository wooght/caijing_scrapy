# -*- coding: utf-8 -*-
#
# @method   : 组合调场仓库
# @Time     : 2018/2/2
# @Author   : wooght
# @File     : zuhe_change.py


from ..Db import *

select_volumns = [zuhe_change.c.code_id, zuhe_change.c.zh_symbol, zuhe_change.c.updated_at, zuhe_change.c.target_weight,
                  zuhe_change.c.change_status]

def one(code_id):
    s = select(select_volumns).where(zuhe_change.c.code_id == code_id)
    r = conn.execute(s)
    return r.fetchall()


def all():
    s = select(select_volumns)
    r = conn.execute(s)
    return r.fetchall()