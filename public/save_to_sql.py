# -*- coding:utf-8 -*-
import datetime
import json
import sqlsoup
from config import Config

db = sqlsoup.SQLSoup(Config.SURL)

class Save_to_sql():

    def __init__(self,site,account,sentry=None):

        #站点名称 site
        self.site = site #站点名称就是表名称
        #登陆名称 account
        self.account = account

        self._sentry = sentry

        #连接对应的表
        self.table = db.entity('export_tasks')

        self.zt_table = db.entity('zt')

        self.infoname_table = db.entity('infoname')


    #插入一条新的记录
    def insert_new(self,ztID,kjqj,infonameID,infodata):

        if type(infodata) != str:
            infodata = json.dumps(infodata)

        #若已经存在数据，将其清空，再重新插入
        if self.table.filter_by(infoname_id=infonameID,zt_id=ztID,kjqj=kjqj,site=self.site).count():
            old_set = self.table.filter_by(infoname_id=infonameID,zt_id=ztID,kjqj=kjqj,site=self.site).one()
            db.delete(old_set)

        new_set = {
            'site':self.site,
            'account':self.account,
            'zt_id':ztID,
            'infoname_id':infonameID,
            'infodata':'',
            'kjqj':kjqj
        }

        try:
            the_set = self.table.insert(**new_set)
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()

        #然后更新
        try:
            the_set.infodata = infodata
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()

    def is_finished(self,ztname):
        '''
        # 判断导出完成，直接忽略
        :return:
        '''

        if self.zt_table.filter_by(ztname=ztname, site=self.site).count():
            zt = self.zt_table.filter_by(ztname=ztname, site=self.site).one()
            stat = zt.status
        else:
            stat = ''

        if '导出完成' in stat:
            return False
        else:
            return True

    #插入一条账套信息
    def init_zt(self,ztname,finished_time='',status=''):
        start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 不重复插入字段名称
        if self.zt_table.filter_by(ztname=ztname, site=self.site).count():
            zt = self.zt_table.filter_by(ztname=ztname, site=self.site).one()
            zt.finished_time = finished_time
            zt.start_time = start_time
            zt.status = status
        else:
            new_set = {
                'ztname':ztname,
                'site':self.site,
                'start_time':start_time,
                'finished_time':finished_time,
                'status':status
            }
            # 定义字段的名称
            zt = self.zt_table.insert(**new_set)
            try:
                db.commit()
            except Exception as e:
                if self._sentry:
                    self._sentry.captureException()
                db.rollback()

        return zt


    def update_zt_status(self,zt,msg):
        '''更新账套'''
        zt.status = str(msg)

        try:
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()


    def update_zt_finised_time(self,zt):

        finished_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        zt.finished_time = str(finished_time)

        try:
            db.commit()
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            db.rollback()


    def init_infoname(self,info_name):

        #不重复插入字段名称
        if self.infoname_table.filter_by(infoname=info_name,site=self.site).count():
            infoname = self.infoname_table.filter_by(infoname=info_name, site=self.site).one()
        else:
            # 定义字段的名称
            infoname = self.infoname_table.insert(infoname=info_name,site=self.site)
            try:
                db.commit()
            except Exception as e:
                if self._sentry:
                    self._sentry.captureException()
                db.rollback()

        return infoname

    def find_zt(self,ztList):
        pass


if __name__ == '__main__':
    sql = Save_to_sql('kungeek', '12345678')
    sql.init_zt('我的公司',status='start')
