# -*- coding: utf-8 -*-
#
# @method   : 缓存,序列化
# @Time     : 2018/1/27
# @Author   : wooght
# @File     : marshal_cache.py

import marshal


class data_cache(object):

    @staticmethod
    def save_marshal(file_path, ms_str):
        f = open(file_path, 'wb')
        marshal.dump(ms_str, f)
        f.close()

    @staticmethod
    def get_marshal(file_path):
        try:
            f = open(file_path, 'rb')
            arr = marshal.load(f)
            f.close()
            return arr
        except:
            return False
