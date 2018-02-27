# -*- coding: utf-8 -*-
#
# @method   : 结果导向情绪分类
# @Time     : 2018/2/27
# @Author   : wooght
# @File     : result_dx_nlp.py

import os
import sys

sys.path.append(os.path.dirname(__file__) + '/../../')

from model import companies
from factory.basedata import basedata
from factory.data_analyse.dd_pct import dd_pct
from common import wfunc
from model import Db as T
from analyse.common import *
from analyse.NLP.participle import pp
from analyse.NLP.semantics import NB

f_quotes = basedata()
all_company = companies.all_codenames()
all_codes = {}
for code in all_company:
    tmp_code = dict(code)
    all_codes[tmp_code['name']] = tmp_code['codeid']

start_day = wfunc.time_num('2017-12-01', '%Y-%m-%d')
end_day = wfunc.time_num('2017-12-12', '%Y-%m-%d')

sz_quotes = f_quotes.select_quotes(1000001, True)
allow_dates = list(sz_quotes['datatime'])

ddpct = dd_pct()
ddpct.select_all()
allow_codes = ddpct.have_dd(260)

nb = NB()


quotes = {}
for i in all_codes.items():
    if i[1] in allow_codes:
        try:
            tmp_quotes = f_quotes.select_quotes(i[1], True)
            tmp_quotes['datatime'] = f_quotes.pd.to_datetime(tmp_quotes['datatime'])
            tmp_quotes.sort_values(by='datatime', ascending=True, inplace=True)
            tmp_quotes.reset_index(inplace=True)
            del tmp_quotes['index']
            quotes[i[0]] = tmp_quotes
        except IndexError:
            continue

print(quotes)
Table = T.news
def allarticles():
    s = T.select([Table.c.body,Table.c.title,Table.c.put_time,Table.c.id,Table.c.title]).where(Table.c.put_time > start_day).where(Table.c.put_time < end_day)
    r = T.conn.execute(s)
    return r.fetchall()
pos = {}
pos['total'] = 0
neg = {}
neg['total'] = 0
all_news = allarticles()
for news in all_news:
    put_time = wfunc.the_day(int(dict(news)['put_time']))
    if put_time not in allow_dates:
        continue
    body = dict(news)['body']
    plate, company = get_index(body)
    ju = pp.cut_ju(body)
    if len(company) > 0:
        for c in company.items():
            charts = c[0]
            if charts not in quotes:
                continue
            for j in ju:
                if charts in j:
                    if len(charts) * 3 > len(j):
                        continue
                    words = nb.pp(j)
                    q = quotes[charts]
                    the_index = q[q['datatime'] == put_time].index[0]  # index格式为Int64Index([0], dtype='int64')
                    try:
                        cha = q.loc[the_index, 'shou'] - q.loc[the_index+5, 'shou']
                    except ValueError:
                        cha = 0
                    if cha > 0:
                        for word in words:
                            if word[0] not in pos:
                                pos[word[0]] = 1
                            else:
                                pos[word[0]] += 1
                            pos['total'] += 1
                    elif cha < 0:
                        for word in words:
                            if word[0] not in neg:
                                neg[word[0]] = 1
                            else:
                                neg[word[0]] += 1
                            neg['total'] += 1

result = {}
result['pos'] = pos
result['neg'] = neg

for i in pos.items():
    print(i)
print('pos total:', pos['total'])

print('*' * 100)

for i in neg.items():
    print(i)
print('neg total', neg['total'])


