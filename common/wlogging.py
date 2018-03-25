# -*- coding: utf-8 -*-
#
# @method   : 本系统日志输出模块
# @Time     : 2017/11/18
# @Author   : wooght
# @File     : wlogging.py

import logging

# 创建独立的logger
lg = logging.getLogger('wooght')
lg.setLevel(logging.INFO)
sh = logging.StreamHandler()    # 输出到控制台的handler
sh.setFormatter(logging.Formatter(fmt='%(asctime)s :: %(message)s', datefmt='%d-%H:%M:%S'))
lg.addHandler(sh)


class wlg:

    @staticmethod
    def e(message):
        lg.info(message)

    @staticmethod
    def error(message):
        lg.warning(message)
