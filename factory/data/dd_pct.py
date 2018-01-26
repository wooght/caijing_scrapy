# -*- coding: utf-8 -*-
#
# @method   : 主力占比统计排名
# @Time     : 2018/1/20
# @Author   : wooght
# @File     : dd_pct.py

import os
import sys

sys.path.append(os.path.dirname(__file__)+'/../../')

from factory.basedata import basedata
from model import ddtj, companies
from factory.data_analyse.ddtj_analyse import ddtj_analyse


class dd_pct(basedata):
    dd_repository = object
    allcode = []

    def select_all(self, start_t=None):
        if start_t is not None:
            dd_repository = ddtj.all_t(start_t)
        else:
            dd_repository = ddtj.all()
        dd_dict = []
        for i in dd_repository:
            dd_dict.append(dict(i))
        self.dd_repository = self.pd.DataFrame(dd_dict)


    def select_companyies(self):
        cplist = []
        for i in companies.all_codenames():
            cplist.append(dict(i))
        self.cps = self.pd.DataFrame(cplist)
        self.cps['code_id'] = self.cps['codeid']
        del self.cps['codeid']


    #  大单占比前100
    def have_dd(self, days):
        pct_mean = self.dd_repository.groupby('code_id', as_index=False)['totalvolpct'].agg({'pctmean': 'mean'})
        pct_count = self.dd_repository.groupby('code_id', as_index=False)['totalvolpct'].agg({'pctcount': 'count'})
        tmp_pd = self.pd.merge(pct_mean, pct_count, on=['code_id'], how='left')
        last_pd = tmp_pd[tmp_pd.pctmean > 0]  # 筛选有大单的数据
        total_day = last_pd.pctcount.max()
        the_data = last_pd[last_pd.pctcount >= days]
        pctsort = the_data.sort_values('pctmean')
        self.pctsort = pctsort
        return list(pctsort.iloc[-5:, :].code_id)


# 回测结果统计
if __name__ == '__main__':
    var_dd = dd_pct()
    var_dd.select_all()
    code_100 = var_dd.have_dd(260)

    #  回测汇总
    total_income = 0
    total_jia = 0
    total_position = 0
    dd = ddtj_analyse()

    max_income = {'id': 0, 'income': 0}
    min_income = {'id': 0, 'income': 0}

    s_all = []
    k_all = []
    for id in code_100:
        dd.select_ddtj(str(id))
        dd.BACKPROBE(True)
        is_times = dd.web_api()
        income = is_times['income']
        total_income += income
        total_jia += is_times['jia_num']
        total_position += len(is_times['hc'])
        id_income = {'id': id, 'income': income, 'max': is_times['max_income']['max'], 'min': is_times['max_income']['min']}
        if income > max_income['income']:
            max_income = id_income
        elif income < min_income['income']:
            min_income = id_income
        if income > 0:
            s_all.append(id_income)
        elif income < 0:
            k_all.append(id_income)

    print('total_income:', total_income, '\t total_jia:', total_jia)
    print('max:', max_income)
    print('min', min_income)
    print('s_all_nums:', len(s_all))
    for i in s_all:
        print('code:', i['id'], '\t'*(2 if i['id']<100000 else 1), 'in:', i['income'], 'max:', i['max'], 'min:', i['min'])

    print('k_all_nums:', len(k_all))
    for i in k_all:
        print('code:', i['id'], '\t' * (2 if i['id'] < 100000 else 1), 'in:', i['income'], 'max:', i['max'], 'min:',
              i['min'])
