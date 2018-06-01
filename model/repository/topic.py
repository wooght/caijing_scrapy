# encoding utf-8
#
# model.topic
# by wooght 2017-11

from ..Db import *


def all():
    s = select([topic.c.body, topic.c.id])
    r = conn.execute(s)
    return r.fetchall()


def all_url():
    s = select([topic.c.url])
    r = conn.execute(s)
    return r.fetchall()


def one(id):
    s = select([topic.c.body, topic.c.id, topic.c.title]).where(topic.c.id == id)
    r = conn.execute(s)
    r_str = r.fetchall()[0]
    return r_str


def up(id, arr):
    u = topic.update().where(topic.c.id == id).values(arr)
    r = conn.execute(u)
    if (r.rowcount > 0):
        return True
    else:
        return False


# 查company codeid
def s_company_id(str):
    s = select([listed_company.c.codeid]).where(listed_company.c.name.like(str))
    r = conn.execute(s)
    result = r.fetchall()
    return result[0][0]


# 查plate plateid
def s_plate_id(str):
    s = select([listed_plate.c.plateid]).where(listed_plate.c.name.like(str))
    r = conn.execute(s)
    result = r.fetchone()
    if result:
        return result[0]
    else:
        return 0
