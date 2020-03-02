# -*- coding: utf-8 -*-
import time

from public.duboo_telnet import callBack
from manage import pool
from public.save_to_sql import Save_to_sql

from yiqidai.NewViews import GetInfo


# from celery_17DZ import celery
# @celery.task(name='yiqidai')
def taskExport(login_info,ztList,site,callback_ip):

    browser = pool.get_browser("chrome", 'yiqidai')

    #取出数据
    account = login_info['account']
    to_sql = Save_to_sql(site, account)
    getInfo = GetInfo(browser,to_sql=to_sql)

    #登陆
    i = 1
    while True:
        msg = getInfo.login(login_info)
        if msg == '登陆成功':
            break
        elif msg == '账号和密码不匹配,请重新输入':
            return
        elif msg == '账号已停用或合同未审核通过':
            return
        elif msg == '账号不存在或已停用':
            return
        elif i>4:
            return '错误次数过多,需人工介入'
        elif msg == '验证码错误,请重新输入':
            i+=1
            continue

    time.sleep(0.5)

    ztData = getInfo.getAllzt()
    for z in ztData:
        params = {
            'customerId':z['customerId'],
            'accountSetId':z['accountSetId'],
            'customerName':z['customerName'],
            'customerShortName':z['customerName']
        }
        accountSetId = z['accountSetId']
        customerId = z['customerId']
        companyName = z['customerFullName'].strip()

        if companyName not in ztList: #判断是否在传递过来的账套里面
            continue

        #创建zt
        zt = to_sql.init_zt(companyName,status='start')
        zt_id = zt.id

        #切换公司
        QjList = getInfo.switchZt(params)
        #凭证
        try:
            msg = getInfo.voucher(QjList,zt_id,'凭证')
            to_sql.update_zt_status(zt,msg)
        except Exception as e:
            raise e
        time.sleep(0.5)

        # 现金流量
        try:
            msg = getInfo.xjll(QjList, zt_id,'现金流量')
            to_sql.update_zt_status(zt, msg)
        except Exception as e:
            raise e
        time.sleep(0.5)

        #科目余额表
        try:
            msg = getInfo.kmsheet(QjList,zt_id,'科目余额表')
            to_sql.update_zt_status(zt,msg)
        except Exception as e:
            raise e
        time.sleep(0.5)

        #辅助核算余额表  注释说明：辅助核算余额表不用抓取，科目余额里可以解析出来
        # try:
        #     msg = getInfo.fzhssheet(QjList, zt_id)
        #     to_sql.update_zt_status()(zt,msg)
        # except Exception as e:
        #     raise e
        # time.sleep(0.5)

        #基础设置
        try:
            msg = getInfo.settings(customerId,zt_id,accountSetId,QjList,'基础设置')
            to_sql.update_zt_status(zt,msg)
        except Exception as e:
            raise e
        time.sleep(0.5)

        # 记录一个账套导出成功
        msg = '%s 导出完成'%companyName
        try:
            to_sql.update_zt_status(zt,msg)
            to_sql.update_zt_finised_time(zt)
        except Exception as e:
            raise e

        # 进行回调 回调参数：db_name,collection,_id
        if not callback_ip:
            callback_host = ''
            callback_port = ''
        else:
            callback_host = callback_ip[:14]
            callback_port = callback_ip[15:]

        resp = callBack(site,callback_host,callback_port)


    #任务完成后，断开浏览器的连接
    pool.close_browser(browser)


if __name__ == '__main__':
    taskExport()