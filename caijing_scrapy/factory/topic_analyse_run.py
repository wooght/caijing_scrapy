#encoding utf-8
#
# 计算tpic文章语义
# by Wooght
# 2017-11
#

import sys,io
dir = __file__.split('\\');del dir[-2:];path = '/'.join(dir);sys.path.append(path)
from model import topic
from analyse.pipeline_article_analyse import article_analyse
import model.Db as T
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

def all():
    s = T.select([T.topic.c.body,T.topic.c.id]).where(T.topic.c.id==24130)
    r = T.conn.execute(s)
    return r.fetchall()
analyse = article_analyse()
#运行入口
news = all()
print(news)
for one in news:
    item = {}
    item['body'] = one[0]
    analyse.run(item)
    del item['body']
    print(item)
    u = T.topic.update().where(T.topic.c['id']==one[1]).values(item)
    r = T.conn.execute(u)
