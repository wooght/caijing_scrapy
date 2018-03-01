# -*- coding: utf-8 -*-
#
# @method   : 末日占比/状态排行接口
# @Time     : 2018/1/26
# @Author   : wooght
# @File     : ddtop100.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.data_analyse import *
from common import wfunc

day = wfunc.today(strtime=False)
file_path = os.path.dirname(__file__) + '/cache/ddtop100' + str(day) + '.w'


class ddtop100(dd_pct):

    def api(self):
        ms_list = data_cache.get_marshal(file_path)
        if ms_list:
            return ms_list
        else:
            self.select_all(wfunc.before_day(60))  # 查询50天前以来的数据
            codes = self.have_dd(30)  # 查询拥有大单30天以上的
            self.select_companyies()
            ddmath = dd_math()
            alldd = ddmath.select_alldd()
            self.dd_repository = alldd
            dd_df_dict = {}
            for id in codes:
                dd_df_dict[id] = alldd[alldd.code_id == id].copy()
            last_df = ddmath.quotes_install(dd_df_dict)
            backprobe = dd_backprobe()
            result = backprobe.last_probe(last_df)
            result_list = []
            for id in result:
                status = result[id]
                names = self.cps[self.cps.code_id == id]
                name = names.iloc[0]['name']
                pct = self.pctsort[self.pctsort.code_id == id].iloc[0]['pctmean']
                result_list.append([str(id), name.encode('utf-8'), float_nums(status[0]),
                                    float_nums(status[1]), float_nums(pct)])
            data_cache.save_marshal(file_path, result_list)
            return result_list


run = ddtop100()
result_data = run.api()
print(result_data)