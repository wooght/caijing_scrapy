# -*- coding: utf-8 -*-
#
# 错误响应
# by wooght 2017-11
#
class Werror(Exception):
    def __init__(self,value='Werror'):
        Exception.__init__(self,value)
