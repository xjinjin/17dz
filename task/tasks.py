# -*- coding:utf-8 -*-

from task import celery_app
from App import app
import time
from yiqidai.NewViews import GetInfo as yiqidai_GetInfo
from yunzhangfang.NewViews import GetInfo as yunzhangfang_GetInfo
from huisuanzhang.NewViews import GetInfo as kungeek_GetInfo
from public.duboo_telnet import callBack
from public.save_to_sql import Save_to_sql


# 初始化浏览器池子
from public.pool import PoolOptions,Pool
options = PoolOptions()
pool = Pool(options)

#使用sentry监听异常
from raven.contrib.flask import Sentry


@celery_app.task(name='export_out_datawisee')
def taskExport_datawisee_out(login_info,ztList,site,callback_ip):

    # browser = DockerForBrowsers(conn_url=Config.QMX_CHROME_URL).connect_to_browser()
    browser = pool.get_browser('chrome','datawisee')
    sentry = Sentry(app,dsn='https://cc465b09e4004bd790db724a7d4252eb:6f73513a850d4e26b34612de0a08f7c9@192.168.20.244:9000//6')

    #取出数据
    account = login_info['account']
    to_sql = Save_to_sql(site, account)
    getInfo = yiqidai_GetInfo(browser,to_sql=to_sql)

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
    new_ztlist = []
    for zt in ztData:
        new_ztlist.append(zt.get('customerFullName','').strip())
    # 判断需要导出的账套是否存在
    for zz in ztList:
        if zz not in new_ztlist:
            # 创建zt
            zt = to_sql.init_zt(zz, status='账套不存在')

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

        if not to_sql.is_finished(companyName): #判断是否已经导出成功，忽略
            # 成功之后，直接回调
            to_callback(site, account, companyName, callback_ip=callback_ip)
            continue

        #创建zt
        zt = to_sql.init_zt(companyName,status='start')
        zt_id = zt.id

        #切换公司
        QjList = getInfo.switchZt(params)
        #凭证
        try:
            msg = getInfo.voucher(QjList,zt_id,'凭证')
        except Exception as e:
            msg = '获取凭证失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        # 现金流量
        try:
            msg = getInfo.xjll(QjList, zt_id,'现金流量')
        except Exception as e:
            msg = '获取现金流量失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #科目余额表
        try:
            msg = getInfo.kmsheet(QjList,zt_id,'科目余额表')
        except Exception as e:
            msg = '获取科目余额表失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #辅助核算余额表  注释说明：辅助核算余额表不用抓取，科目余额里可以解析出来
        # try:
        #     msg = getInfo.fzhssheet(QjList, zt_id)
        # except Exception as e:
        #     msg = '获取辅助核算余额失败:%s' % str(e)
        #     to_sql.update_zt_status(zt, msg)
        #     sentry.captureException()
        # else:
        #     to_sql.update_zt_status(zt, msg)
        # time.sleep(0.5)

        #基础设置
        try:
            msg = getInfo.settings(customerId,zt_id,accountSetId,QjList,'基础设置')
        except Exception as e:
            msg = '获取基础设置失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        # 记录一个账套导出成功
        msg = '%s 导出完成'%companyName
        to_sql.update_zt_status(zt,msg)
        to_sql.update_zt_finised_time(zt)


        # 进行回调 回调参数：db_name,collection,_id
        to_callback(site, account, companyName, callback_ip=callback_ip)
        print(companyName)

    #任务完成后，断开浏览器的连接
    pool.close_browser(browser)


@celery_app.task(name='export_out_yiqidai')
def taskExport_yiqidai_out(login_info,ztList,site,callback_ip):
    print('++++yiqidai_in++++++')
    # browser = DockerForBrowsers(conn_url=Config.YQDZ_CHROME_URL).connect_to_browser()
    browser = pool.get_browser('chrome', 'yiqidai')
    sentry = Sentry(app,dsn='https://cc465b09e4004bd790db724a7d4252eb:6f73513a850d4e26b34612de0a08f7c9@192.168.20.244:9000//6')

    #取出数据
    account = login_info['account']
    to_sql = Save_to_sql(site, account)
    getInfo = yiqidai_GetInfo(browser,to_sql=to_sql)

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
    new_ztlist = []
    for zt in ztData:
        new_ztlist.append(zt.get('customerFullName','').strip())
    # 判断需要导出的账套是否存在
    for zz in ztList:
        if zz not in new_ztlist:
            # 创建zt
            zt = to_sql.init_zt(zz, status='账套不存在')

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

        if not to_sql.is_finished(companyName): #判断是否已经导出成功，忽略
            #导出成功，直接回调
            to_callback(site,account,companyName,callback_ip=callback_ip)
            continue

        #创建zt
        zt = to_sql.init_zt(companyName,status='start')
        zt_id = zt.id

        #切换公司
        QjList = getInfo.switchZt(params)

        #凭证
        print('++++凭证++++')
        try:
            msg = getInfo.voucher(QjList,zt_id,'凭证')
        except Exception as e:
            msg = '获取凭证失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        # 现金流量
        try:
            msg = getInfo.xjll(QjList, zt_id,'现金流量')
        except Exception as e:
            msg = '获取现金流量失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #科目余额表
        try:
            msg = getInfo.kmsheet(QjList,zt_id,'科目余额表')
        except Exception as e:
            msg = '获取科目余额表失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #辅助核算余额表  注释说明：辅助核算余额表不用抓取，科目余额里可以解析出来
        # try:
        #     msg = getInfo.fzhssheet(QjList, zt_id)
        # except Exception as e:
        #     msg = '获取辅助核算余额失败:%s' % str(e)
        #     to_sql.update_zt_status(zt, msg)
        #     sentry.captureException()
        # else:
        #     to_sql.update_zt_status(zt, msg)
        # time.sleep(0.5)

        #基础设置
        try:
            msg = getInfo.settings(customerId,zt_id,accountSetId,QjList,'基础设置')
        except Exception as e:
            msg = '获取基础设置失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        # 记录一个账套导出成功
        msg = '%s 导出完成'%companyName
        to_sql.update_zt_status(zt,msg)
        to_sql.update_zt_finised_time(zt)


        # 进行回调 回调参数：db_name,collection,_id
        to_callback(site, account, companyName, callback_ip=callback_ip)
        print(companyName)

    #任务完成后，断开浏览器的连接
    pool.close_browser(browser)


@celery_app.task(name='export_out_kungeek')
def taskExport_kungeek_out(login_info,ztList,site,callback_ip):
    print('++++kungeek_in+++++')
    # browser = DockerForBrowsers(conn_url=Config.KUNGEEK_CHROME_URL).connect_to_browser()
    browser = pool.get_browser('chrome', 'kungeek')
    sentry = Sentry(app,dsn='https://cc465b09e4004bd790db724a7d4252eb:6f73513a850d4e26b34612de0a08f7c9@192.168.20.244:9000//6')

    # 取出数据
    account = login_info['account']
    to_sql = Save_to_sql(site, account)
    getInfo = kungeek_GetInfo(browser, to_sql=to_sql)

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
    new_ztlist = []
    for zt in ztData:
        new_ztlist.append(zt.get('name', '').strip())
    # 判断需要导出的账套是否存在
    for zz in ztList:
        if zz not in new_ztlist:
            # 创建zt
            zt = to_sql.init_zt(zz, status='账套不存在')

    for z in ztData:
        ztId = z['ztId']
        khId = z['id']
        companyName = z['name'].strip()

        if companyName not in ztList: #判断是否在传递过来的账套里面
            continue

        if not to_sql.is_finished(companyName): #判断是否已经导出成功，忽略
            # 成功之后，直接回调
            to_callback(site, account, companyName, callback_ip=callback_ip)
            continue

        # 创建zt
        zt = to_sql.init_zt(companyName, status='start')
        zt_id = zt.id

        QjList = getInfo.switchZt(ztId,khId)

        #凭证
        print('+++++开始凭证++++')
        try:
            msg = getInfo.voucher(QjList,ztId,zt_id,'凭证')
        except Exception as e:
            msg = '获取凭证失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #科目余额表
        try:
            msg = getInfo.kmsheet(QjList,ztId,zt_id,'科目余额表')
            to_sql.update_zt_status(zt,msg)
        except Exception as e:
            msg = '获取科目余额表失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #会计科目
        try:
            msg = getInfo.kjkmsheet(ztId,zt_id,'会计科目')
            to_sql.update_zt_status(zt,msg)
        except Exception as e:
            msg = '获取会计科目失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #基础设置
        try:
            msg = getInfo.settings(ztId,zt_id,'基础设置')
        except Exception as e:
            msg = '获取基础设置失败:%s' % str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        # 记录一个账套导出成功
        msg = '%s 导出完成'%companyName
        to_sql.update_zt_status(zt, msg)
        to_sql.update_zt_finised_time(zt)


        # 进行回调 回调参数：db_name,collection,_id
        to_callback(site, account, companyName, callback_ip=callback_ip)
        print(companyName)


    #任务完成后，断开浏览器的连接
    pool.close_browser(browser)


@celery_app.task(name='export_out_yunzhangfang')
def taskExport_yunzhangfang_out(login_info,ztList,site,callback_ip):

    browser = pool.get_browser('chrome', 'yunzhangfang')
    sentry = Sentry(app, dsn='https://cc465b09e4004bd790db724a7d4252eb:6f73513a850d4e26b34612de0a08f7c9@192.168.20.244:9000//6')
    # browser = DockerForBrowsers(conn_url=Config.YZF_CHROME_URL).connect_to_browser()

    # 取出数据
    account = login_info['account']
    to_sql = Save_to_sql(site, account,sentry)
    getInfo = yunzhangfang_GetInfo(browser,to_sql=to_sql,sentry=sentry)


    #登陆
    i = 1
    while True:
        msg = getInfo.login(login_info)
        if msg == '登陆成功':
            break
        elif msg == '账号和密码不匹配,请重新输入':
            return
        elif i>4:
            return '错误次数过多,需人工介入'
        elif msg == '验证码错误,请重新输入':
            i+=1
            continue

    time.sleep(0.5)


    ztData = getInfo.getAllzt()
    new_ztlist = []
    for zt in ztData:
        new_ztlist.append(zt.get('qymc', '').strip())
    # 判断需要导出的账套是否存在
    for zz in ztList:
        if zz not in new_ztlist:
            # 创建zt
            zt = to_sql.init_zt(zz, status='账套不存在')

    for zt in ztData:
        currentKjnd = zt['currentKjnd']
        currentKjqj = zt['currentKjqj']
        qyid = zt['qyid']
        companyName = zt['qymc'].strip()

        #拼接url
        # getInfo.createUrl(currentKjnd,currentKjqj,qyid)

        if companyName not in ztList: #判断是否在传递过来的账套里面
            continue

        if not to_sql.is_finished(companyName): #判断是否已经导出成功，忽略
            #成功之后，直接回调
            to_callback(site, account, companyName, callback_ip=callback_ip)
            continue

        # 创建zt
        zt = to_sql.init_zt(companyName, status='start')
        zt_id = zt.id

        #获取所有期间
        Qjlist,ztdm = getInfo.dates(qyid, currentKjnd, companyName)
        time.sleep(0.5)

        #企业信息
        try:
            msg = getInfo.company_info(qyid,companyName,zt_id,'企业信息')
        except Exception as e:
            msg = '获取企业信息失败:%s'%str(e)
            to_sql.update_zt_status(zt,msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt,msg)
        time.sleep(0.5)

        #会计科目
        try:
            msg = getInfo.kjkm(ztdm,qyid,companyName,currentKjnd,currentKjqj,zt_id,'会计科目')
        except Exception as e:
            msg = '获取会计科目失败:%s'%str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #凭证
        try:
            msg = getInfo.voucher(Qjlist,ztdm,zt_id,'凭证')
        except Exception as e:
            msg = '获取凭证失败:%s'%str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)

        time.sleep(0.5)

        #币别列表
        Bilist = getInfo.bibie(ztdm)
        time.sleep(0.5)

        #科目余额
        try:
            msg = getInfo.kmye(Qjlist,ztdm,qyid,Bilist,zt_id,'科目余额')
        except Exception as e:
            msg = '获取科目余额失败:%s'%str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)
        time.sleep(0.5)

        #获取数量金额科目余额表
        try:
           getInfo.sljeye(Qjlist,ztdm,qyid,Bilist,zt_id,'数量金额科目余额表')
        except Exception as e:
            msg = '获取数量金额科目余额表失败:%s'%str(e)
            to_sql.update_zt_status(zt, msg)
            sentry.captureException()
        else:
            to_sql.update_zt_status(zt, msg)

        # 记录一个账套导出成功
        msg = '%s 导出完成' % companyName
        to_sql.update_zt_status(zt, msg)
        to_sql.update_zt_finised_time(zt)

        # 进行回调 回调参数：db_name,collection,_id
        to_callback(site, account, companyName, callback_ip=callback_ip)

    # 任务完成后，断开浏览器的连接
    pool.close_browser(browser)


def to_callback(site, account, companyName, callback_ip=''):
    '''进行回调'''
    sentry = Sentry(app,dsn='https://cc465b09e4004bd790db724a7d4252eb:6f73513a850d4e26b34612de0a08f7c9@192.168.20.244:9000//6')

    # 进行回调 回调参数：db_name,collection,_id
    if not callback_ip:
        callback_host = ''
        callback_port = ''
    else:
        callback_host = callback_ip.split(':')[0]
        callback_port = callback_ip.split(':')[1]

    try:
        callBack(site, account, companyName, callback_host=callback_host, callback_port=callback_port)
    except Exception as e:
        sentry.captureException()