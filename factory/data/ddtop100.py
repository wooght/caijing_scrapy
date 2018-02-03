# -*- coding: utf-8 -*-
#
# @method   : 末日占比/状态排行接口
# @Time     : 2018/1/26
# @Author   : wooght
# @File     : ddtop100.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.data_analyse import dd_pct
from factory.data_analyse import ddtj_analyse
from factory.data_analyse import data_cache
from factory.data_analyse import float_nums
from common import wfunc

day = wfunc.today(strtime=False)
file_path = os.path.dirname(__file__) + '/cache/ddtop100' + str(day) + '.w'


class ddtop100(dd_pct):

    def api(self):
        ms_list = data_cache.get_marshal(file_path)
        if ms_list:
            return ms_list
        else:
            self.select_all(wfunc.before_day(50))  # 查询50天前以来的数据
            codes = self.have_dd(30)  # 查询拥有大单30天以上的
            self.select_companyies()
            dd = ddtj_analyse()
            result_list = []
            for id in codes:
                dd.select_ddtj(str(id), '2017-12-01')
                status = dd.last_probe()
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