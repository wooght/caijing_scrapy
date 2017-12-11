#encoding utf-8
#
# 计算tpic文章语义
# by Wooght
# 2017-11
#

import sys,io
dir = __file__.split('\\');del dir[-3:];path = '/'.join(dir);sys.path.append(path)
from model import topic
from analyse.pipeline_article_analyse import article_analyse
import model.Db as T
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gbk') #改变标准输出的默认编码
Table = T.news
def all():
    s = T.select([Table.c.body,Table.c.title,Table.c.put_time,Table.c.id,Table.c.title])
    r = T.conn.execute(s)
    return r.fetchall()
analyse = article_analyse()
#运行入口
news = all()
for one in news:
    one = dict(one)
    one['article_id'] = one['id']
    one['article_type'] = 2 #文章分类,1位topic,2位news
    result = analyse.run(one)
    if(len(result)>0):
        u = T.attitude_relation.insert()
        r = T.conn.execute(u,result)
        print(result)
