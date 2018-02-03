# -*- coding: utf-8 -*-
#
# @method   : 主力大单回测结果综合展示api
# @Time     : 2018/1/27
# @Author   : wooght
# @File     : dd_backprobe.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.data_analyse import *

from common import wfunc

day = wfunc.today(strtime=False)
file_path = os.path.dirname(__file__) + '/cache/ddbackprob' + str(day) + '.w'


# 回测结果统计
if __name__ == '__main__':
    ms_list = data_cache.get_marshal(file_path)
    if ms_list:
        print(ms_list)
    else:
        var_dd = dd_pct()
        var_dd.select_all(wfunc.before_day(50))
        var_dd.select_companyies()
        code_100 = var_dd.have_dd(30)
        var_zh = zuhe_math()
        zh_focus = var_zh.group_mean()

        #  回测汇总
        total_income = 0
        total_jia = 0
        total_position = 0
        total_ycome = 0
        total_kcome = 0
        total_ycodes = 0
        total_kcodes = 0
        dd = ddtj_analyse()

        max_income = {'id': 0, 'income': 0}
        min_income = {'id': 0, 'income': 0}

        s_all = []
        for id in code_100:
            if id not in zh_focus:
                continue
            dd.select_ddtj(str(id), start_date='2017-12-01')
            dd.BACKPROBE(True)
            is_times = dd.web_api()
            income = is_times['income']
            total_income += income
            total_jia += is_times['jia_num']
            total_position += len(is_times['hc'])
            name = var_dd.cps[var_dd.cps['code_id'] == id].iloc[0]['name']
            id_income = {'name': name.encode('utf-8'), 'id': str(id), 'income': float_nums(income),
                         'max': float_nums(is_times['max_income']['max']),
                         'min': float_nums(is_times['max_income']['min'])}
            if income > max_income['income']:
                max_income = id_income
            elif income < min_income['income']:
                min_income = id_income
            if income > 0:
                total_ycome += float_nums(income)
                total_ycodes += 1
            else:
                total_kcome += float_nums(income)
                total_kcodes += 1
            s_all.append(id_income)
        # last_list = sorted(s_all, key=lambda d: d['income'])
        result = {
            'total_income': float_nums(total_income),
            'total_jia': float_nums(total_jia),
            'probe_data': s_all,
            'total_ycome': total_ycome,
            'total_kcome': total_kcome,
            'total_ycodes': total_ycodes,
            'total_kcodes': total_kcodes,
            'strategy': '占比少,带动力小,速率相差更大'.encode('utf-8')
        }
        data_cache.save_marshal(file_path, result)
        print(result)
