# -*- coding: utf-8 -*-
#
# @method   :
# @Time     : 2018/1/24
# @Author   : wooght
# @File     : __init__.py.py

# dd_pct  占比计算
# dd_position 仓位判断
# ddtj_analyse 回测

from .marshal_cache import data_cache
from .ddtj_analyse import ddtj_analyse
from .dd_pct import dd_pct
from .dd_position import dd_position
from .zuhe_math import zuhe_math

def float_nums(num):
    return float('%.2f' % num)