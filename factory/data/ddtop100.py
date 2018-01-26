# -*- coding: utf-8 -*-
#
# @method   : 大单占比排行接口
# @Time     : 2018/1/26
# @Author   : wooght
# @File     : ddtop100.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.data.dd_pct import dd_pct
from factory.data_analyse.ddtj_analyse import ddtj_analyse


class ddtop100(dd_pct):

    def api(self):
        self.select_all('2017-12-01')
        codes = self.have_dd(20)  # 最近20天
        self.select_companyies()
        dd = ddtj_analyse()
        result_list = []
        for id in codes:
            dd.select_ddtj(str(id))
            status = dd.last_probe()
            names = self.cps[self.cps.code_id == id]
            name = names.iloc[0]['name']
            pct = self.pctsort[self.pctsort.code_id == id].iloc[0]['pctmean']
            result_list.append([id, name.encode('utf-8'), status[0], status[1], pct])
        return result_list





a = ddtop100()
b = a.api()
print(b)