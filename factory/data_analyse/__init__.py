# -*- coding: utf-8 -*-
#
# @method   : 数据分析模块
# @Time     : 2018/1/24
# @Author   : wooght
# @File     : __init__.py.py

# dd_pct  占比计算排序
# dd_position 依据大单进出场判断
# ddtj_analyse 大单回测入口
# marshal_cache 缓存模块
# zuhe_math 组合数学模型
# dd_math 大单数学模型
# data_structure/dd_structure 大单分析数据结构
# dd_backprobe 大单回测调度

from .marshal_cache import data_cache
from .ddtj_analyse import ddtj_analyse
from .dd_pct import dd_pct
from .dd_position import dd_position
from .zuhe_math import zuhe_math
from .dd_math import dd_math
from .data_structure import *  # 数据结构
from .dd_backprobe import dd_backprobe


def float_nums(num):
    return float('%.2f' % num)
