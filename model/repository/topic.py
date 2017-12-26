#encoding utf-8
#
# model.topic
# by wooght 2017-11

import model.Db as T

def all():
    s = T.select([T.topic.c.body,T.topic.c.id]).where(T.topic.c.id>21441)
    r = T.conn.execute(s)
    return r.fetchall()

def one(id):
    s = T.select([T.topic.c.body,T.topic.c.id]).where(T.topic.c.id==id)
    r = T.conn.execute(s)
    r_str = r.fetchall()[0]
    return r_str

def up(id,arr):
    u = T.topic.update().where(T.topic.c.id==id).values(arr)
    r = T.conn.execute(u)
    if(r.rowcount>0):
        return True
    else:
        return False

#查company codeid
def s_company_id(str):
    s = T.select([T.listed_company.c.codeid]).where(T.listed_company.c.name.like(str))
    r = T.conn.execute(s)
    result = r.fetchall()
    return result[0][0]

#查plate plateid
def s_plate_id(str):
    s = T.select([T.listed_plate.c.plateid]).where(T.listed_plate.c.name.like(str))
    r = T.conn.execute(s)
    result = r.fetchone()
    return result[0]
