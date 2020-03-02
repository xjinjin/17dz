# -*- coding:utf-8 -*-
import datetime

from bson import ObjectId
from pymongo import MongoClient
from config import Config

class Mongo_save():
    '''存储云账房数据'''
    account = ''
    new_set = {}
    task_set = {}

    def __init__(self, account=None):
        self.conn = MongoClient(Config.MONGO_HOST, Config.MONGO_PORT)
        self.db = self.conn['yunzhangfang']
        # 用户名密码
        self.db.authenticate(name=Config.YUNZHANGFANG_USER, password=Config.YUNZHANGFANG_PWD)
        self.account = account or self.account
        self.task_set = self.db['task_msg']

    def create_dbs(self):
        if self.account:
            new_set = self.db['m_%s' % self.account]

            return new_set

    def save_img(self,data):
        new_set = self.db['img']

        new_set.insert({'img':data})


    def save_zts(self,zts):
        self.new_set = self.create_dbs()
        self.new_set.insert(
            {'账套信息':dict(zts)}
        )

    def create_set(self, company):
        self.new_set = self.create_dbs()
        id = self.new_set.insert_one(
            {company:
                {
                    '凭证': 'none',
                    '科目余额': 'none',
                    '数量金额科目余额': 'none',
                    '会计科目': 'none',
                    '企业信息': {
                        '基本信息': 'none',
                        '国税信息': 'none',
                        '地税信息': 'none'
                    }
                }
            }
        ).inserted_id

        return str(id)


    # 创建任务
    def create_task(self, data, ztList, db_name,callback_ip):
        create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        id = self.task_set.insert_one(
            {'task_info': {
                'login_info': data,
                'zt': ztList,
                'db_name': db_name,
                'callback_ip':callback_ip
            },
                'create_time': create_time,
                'status': '等待执行',
                'start_task': '',
                'finished_task': ''
            }).inserted_id

        return id

    # 更新任务执行时间
    def update_status(self, id, status):
        start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 通过id更新
        self.task_set.update(
            {
                '_id': ObjectId(id)
            },
            {
                '$set': {
                    'status': status,
                    'start_task': start_time
                }
            }
        )

    # 记录任务完成时间
    def task_finished(self, id):
        finished_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.task_set.update(
            {
                '_id': ObjectId(id)
            },
            {
                '$set': {
                    'status': '执行完成',
                    'finished_task': finished_time
                }
            }
        )

    #todo: 将更新的位置作为参数传入，提取为一个函数

    #更新凭证
    def update_voucher(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.凭证' % company: data
                }
            }
        )


    # 更新科目余额表
    def update_kmye(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.科目余额' % company: data
                }
            }
        )


    # 更新数量金额科目余额
    def update_sljeye(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.数量金额科目余额' % company: data
                }
            }
        )


    def update_kjkm(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.会计科目' % company: data
                }
            }
        )


    #更新企业基本信息
    def update_jiben(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.企业信息.基本信息' % company: data
                }
            }
        )

    # 国税信息
    def update_guoshui(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.企业信息.国税信息' % company: data
                }
            }
        )


    # 地税信息
    def update_dishui(self, company, data):
        self.new_set.update(
            {
                '%s' % company: {'$exists': 'true'}
            },
            {
                '$set': {
                    '%s.企业信息.地税信息' % company: data
                }
            }
        )

