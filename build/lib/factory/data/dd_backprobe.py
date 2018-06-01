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
        ddpct = dd_pct()
        ddpct.select_companyies()
        ddmath = dd_math()
        zhmath = zuhe_math()
        zh_focus = zhmath.group_mean()
        alldd = ddmath.select_alldd()
        ddpct.dd_repository = alldd
        codeids = ddpct.have_dd(days=100, nums=400)
        dd_df_dict = {}
        for id in codeids:
            if id not in zh_focus:
                continue
            dd_df_dict[id] = alldd[alldd.code_id == id].copy()

        last_df = ddmath.quotes_install(dd_df_dict)
        backprobe = dd_backprobe()
        result = backprobe.dispatch(last_df, days=0, enddays=0)

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
        for i in codeids:
            if i not in zh_focus:
                continue
            income = result[i].f_total_income()
            total_income += income
            total_jia += (result[i].jia_nums() + result[i].kai_nums())
            name = ddpct.cps[ddpct.cps['code_id'] == result[i].codeid].iloc[0]['name']
            id_income = {'name': name.encode('utf-8'), 'id': str(result[i].codeid), 'income': float_nums(income),
                         'max': float_nums(result[i].f_max_income()),
                         'min': float_nums(result[i].f_min_income())}
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

        web_result = {
            'total_income': float_nums(total_income),
            'total_jia': float_nums(total_jia),
            'probe_data': s_all,
            'total_ycome': total_ycome,
            'total_kcome': total_kcome,
            'total_ycodes': total_ycodes,
            'total_kcodes': total_kcodes,
            'strategy': '占比少,带动力小,速率相差更大'.encode('utf-8')
        }
        data_cache.save_marshal(file_path, web_result)
        print(web_result)
