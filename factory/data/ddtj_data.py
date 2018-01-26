# encoding utf-8
# ##################################
# 大单统计数据组装
# by wooght
# 2017-11
# ##################################

import os
import sys

sys.path.append(os.path.dirname(__file__)+'/../../')

from factory.data_analyse.ddtj_analyse import ddtj_analyse

# 获取参数股票代码
try:
    code_id = sys.argv[1]
except:
    code_id = 601318


if __name__ == '__main__':
    dd = ddtj_analyse()
    dd.select_ddtj(code_id)
    dd.BACKPROBE(True)
    is_times = dd.web_api()
    dd.BACKPROBE(False)
    no_times = dd.web_api()
    result = {
        'is_data': is_times,
        'is_nums': len(is_times['hc']),
        'is_income': round(is_times['income'], 2),
        'is_jia': is_times['jia_num'],
        'no_nums': len(no_times['hc']),
        'no_income': round(no_times['income'], 2),
        'no_jia': no_times['jia_num'],
    }
    print(result)

    # for i in is_times['dd_data']:
    #     print(i)
