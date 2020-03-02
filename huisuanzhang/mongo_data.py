# -*- coding: utf-8 -*-
import datetime

from pymongo import MongoClient
from bson.objectid import ObjectId
from config import Config


class MONGO_SAVE():
    account = ''
    new_set = {}
    task_set = {}

    def __init__(self, conn=None, account=None):
        if isinstance(conn, (MongoClient,)):
            self.conn = conn
        else:
            self.conn = MongoClient(host=Config.MONGO_HOST, port=Config.MONGO_PORT)
        self.db = self.conn['kungeek']
        #用户名密码
        self.db.authenticate(name=Config.KUNGEEK_USER, password=Config.KUNGEEK_PWD)
        self.account = account or self.account
        self.task_set = self.db['task_msg']

    def createDataSet(self):
        if self.account:
            new_set = self.db['m_%s' % self.account]

            return new_set

    def createDocument(self, zt):
        self.new_set = self.createDataSet()

        data = {'%s' % zt:
                    {'凭证': 'none',
                     '科目余额': 'none',
                     '辅助核算余额': 'none',
                     '基础设置': {
                         '科目': 'none',
                         '辅助核算': 'none',
                         '币别': 'none'
                     }
                     }
                }

        id = self.new_set.insert_one(data).inserted_id

        return str(id)

    # 创建任务
    def create_task(self, data, ztList, db_name,callback_ip):
        create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        id = self.task_set.insert_one(
            {'task_info': {
                'login_info': data,
                'zt': ztList,
                'db_name': db_name,
                'callback_ip': callback_ip
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

    # 更新凭证
    def update_voucher(self, company, data):

        self.new_set.update(
            {
                '%s.凭证' % company: 'none'
            },
            {
                '$set': {
                    '%s.凭证' % company: data
                }
            }
        )

    # 更新科目余额表
    def update_kmsheet(self, company, data):

        self.new_set.update(
            {
                '%s.科目余额' % company: 'none'
            },
            {
                '$set': {
                    '%s.科目余额' % company: data
                }
            }
        )

    # 更新辅助核算余额表
    def update_fzsheet(self, company, data):

        self.new_set.update(
            {
                '%s.辅助核算余额' % company: 'none'
            },
            {
                '$set': {
                    '%s.辅助核算余额' % company: data
                }
            }
        )

    # 更新基础设置.科目
    def update_setting_km(self, company, data):

        self.new_set.update(
            {
                '%s.基础设置.科目' % company: 'none'
            },
            {
                '$set': {
                    '%s.基础设置.科目' % company: data
                }
            }
        )

    # 更新基础设置.币别
    def update_setting_bibie(self, company, data):

        self.new_set.update(
            {
                '%s.基础设置.币别' % company: 'none'
            },
            {
                '$set': {
                    '%s.基础设置.币别' % company: data
                }
            }
        )

    # 更新基础设置.辅助核算
    def update_setting_fzhs(self, company, data):

        self.new_set.update(
            {
                '%s.基础设置.辅助核算' % company: 'none'
            },
            {
                '$set': {
                    '%s.基础设置.辅助核算' % company: data
                }
            }
        )
