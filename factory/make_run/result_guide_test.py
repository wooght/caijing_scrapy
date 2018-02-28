# -*- coding: utf-8 -*-
#
# @method   : 结果导向分类查看
# @Time     : 2018/3/1
# @Author   : wooght
# @File     : result_guide_test.py

import os, io
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from factory.data_analyse.marshal_cache import data_cache
cache_file = os.path.dirname(__file__)+'/result_guide.wooght'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码

data = data_cache.get_marshal(cache_file)
pos = data['pos']
neg = data['neg']

for i in pos:
    if i in neg:
        print(i, ':pos:', pos[i], '\t', 'neg:', neg[i])
    else:
        print(i, ':pos:', pos[i], '\t', 'neg:', 0)

print('pos total:', pos['total'], 'len:', len(pos))
print('neg total:', neg['total'], 'len:', len(neg))