# -*- coding: utf-8 -*-
#
# @method   : redis 操作模块
# @Time     : 2018/3/27
# @Author   : wooght
# @File     : Db_redis.py

import redis

pool = redis.ConnectionPool(host='192.168.10.10', port=6379, db=0)  # 连接池
rds = redis.Redis(connection_pool=pool)  #连接,指定连接池