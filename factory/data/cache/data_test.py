# -*- coding: utf-8 -*-
#
# @method   :
# @Time     : 2018/2/6
# @Author   : wooght
# @File     : data_test.py


import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.data_analyse import dd_math
from factory.data_analyse import dd_pct
from factory.data_analyse import dd_backprobe

ddpct = dd_pct()
a = dd_math()

# b = a.select_alldd()
# ddpct.dd_repository = b
# dd_codeid = ddpct.have_dd(260)
dd_df_dict = {}
# for id in dd_codeid:
#     df_tmp = b[b.code_id == id].copy()
#     dd_df_dict[id] = df_tmp

b = a.one_ddtj(600519)
dd_df_dict[600519] = b
last_df = a.quotes_install(dd_df_dict)

backprobe = dd_backprobe()
result = backprobe.dispatch(last_df)
for i in result:
    now_code = result[i].pd
    for n in now_code.itertuples():
        print(n.code_id, n.datatime, n.dd_change, '\t', n.shou_change, '\t', n.income, '\t', n.total_income, '\t',
              n.c_state)
    print(result[i].total_income, result[i].f_total_income(), result[i].f_max_income(), result[i].jia_nums(), result[i].kai_nums())
    print(result[i].start_kai)
