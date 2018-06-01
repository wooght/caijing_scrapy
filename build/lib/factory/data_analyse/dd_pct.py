# -*- coding: utf-8 -*-
#
# @method   : 主力占比统计
# @Time     : 2018/1/20
# @Author   : wooght
# @File     : dd_pct.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.basedata import basedata
from model import ddtj, companies


#  主力占比统计
class dd_pct(basedata):
    dd_repository = object
    allcode = []

    #  查询所有大单数据
    def select_all(self, start_t=None):
        if start_t is not None:
            dd_repository = ddtj.all_t(start_t)
        else:
            dd_repository = ddtj.all()
        dd_dict = []
        for i in dd_repository:
            dd_dict.append(dict(i))
        self.dd_repository = self.pd.DataFrame(dd_dict)

    #  查询所有所有公司codeid,name
    def select_companyies(self):
        cplist = []
        for i in companies.all_codenames():
            cplist.append(dict(i))
        self.cps = self.pd.DataFrame(cplist)
        self.cps['code_id'] = self.cps['codeid']
        del self.cps['codeid']

    #  占比排序取codeid
    #  return list codeid
    def have_dd(self, days, nums=100):
        pct_mean = self.dd_repository.groupby('code_id', as_index=False)['totalvolpct'].agg({'pctmean': 'mean'})
        pct_count = self.dd_repository.groupby('code_id', as_index=False)['totalvolpct'].agg({'pctcount': 'count'})
        tmp_pd = self.pd.merge(pct_mean, pct_count, on=['code_id'], how='left')
        last_pd = tmp_pd[tmp_pd.pctmean > 0]  # 筛选有大单的数据
        the_data = last_pd[last_pd.pctcount >= days]  # 筛选拥有大单天数
        pctsort = the_data.sort_values('pctmean')  # 按照占比排序
        self.pctsort = pctsort
        return list(pctsort.iloc[- nums:, :].code_id)
