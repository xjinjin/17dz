# -*- coding:utf-8 -*-
import logging

from kombu import Exchange
from kombu import Queue

class Config(object):
    """配置信息"""
    DEBUG = False

    '''browser的配置'''
    YQDZ_CHROME_URL = 'http://127.0.0.1:4441/wd/hub'
    KUNGEEK_CHROME_URL = 'http://127.0.0.1:4442/wd/hub'
    YZF_CHROME_URL = 'http://127.0.0.1:4443/wd/hub'
    QMX_CHROME_URL = 'http://127.0.0.1:4444/wd/hub'

    # YQDZ_CHROME_URL = 'http://127.0.0.1:4445/wd/hub'
    # KUNGEEK_CHROME_URL = 'http://127.0.0.1:4446/wd/hub'
    # YZF_CHROME_URL = 'http://127.0.0.1:4447/wd/hub'
    # QMX_CHROME_URL = 'http://127.0.0.1:4448/wd/hub'

    # YQDZ_CHROME_URL = 'http://127.0.0.1:4449/wd/hub'
    # KUNGEEK_CHROME_URL = 'http://127.0.0.1:4450/wd/hub'
    # YZF_CHROME_URL = 'http://127.0.0.1:4451/wd/hub'
    # QMX_CHROME_URL = 'http://127.0.0.1:4452/wd/hub'


    '''mysql的配置'''
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@127.0.0.1:3306/database"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # mongodb配置--------------------------------------------------------------
    # MONGO_HOST = '127.0.0.1'
    MONGO_HOST = '192.168.1.243'
    MONGO_PORT = 27017

    KUNGEEK_USER = 'kungeek'  # 慧算账
    KUNGEEK_PWD = 'kungeek123'

    YQDZ_USER = 'yiqidai'  # 亿企代帐
    YQDZ_PWD = '17DZ123'

    YUNDAIZHANG_USER = 'YDZ'  # 云代账
    YUNDAIZHANG_PWD = 'yundaizhang123'  # 云代账

    YUNZHANGFANG_USER = 'YZF'  # 云账房
    YUNZHANGFANG_PWD = 'yunzhangfang123'  # 云账房


    # duboo回调测试接口配置------------------------------------------------------
    DUBOO_HOST = '192.168.1.79'
    DUBOO_PORT = 20882
    # DUBOO_HOST = '192.168.20.205'


    # sqlsoup url--------------------------------------------------------------
    MYSQL_HOST = '192.168.10.11'
    MYSQL_PORT = 3306
    # SURL = "mysql+pymysql://cic_admin:TaBoq,,1234@{}:{}/cicjust_splinter?charset=utf8&autocommit=true".format(MYSQL_HOST, MYSQL_PORT)
    SURL = "mysql+pymysql://cic_admin:159357a@{}:{}/cicjust_splinter?charset=utf8&autocommit=true".format(MYSQL_HOST, MYSQL_PORT)
    # SURL = "mysql+pymysql://root:mysql@{}:{}/test?charset=utf8&autocommit=true".format(MYSQL_HOST, MYSQL_PORT)


    # 设置默认的日志级别
    LEVEL = logging.ERROR


# 开发模式配置
class DevelopConfig(Config):
    pass


# 生产模式配置
class ProductConfig(Config):
    # 关闭调试信息
    DEBUG = False

    # 开发模式的调试级别
    LEVEL = logging.ERROR


# 测试模式
class TestConfig(Config):
    # 开启测试模式;
    TESTING = True


# 提供统一的访问入口
config_dict = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "test": TestConfig
}
