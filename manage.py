# -*- coding:utf-8 -*-
import json

from celery import signature
from flask import jsonify   # Content-Type: application/json   Content-Type: text/html; charset=utf-8

# celeryApp = Celery(broker=Config.CELERY_BROKER_URL)
# celeryApp.conf.update(app.config)
# celeryApp.autodiscover_tasks(['yiqidai','yunzhangfang','huisuanzhang'])

from flask import request
from raven.contrib.flask import Sentry
from config import Config
# from public.docker_for_browsers import DockerForBrowsers

from App import app
#使用sentry监听异常
from task.main import export_tasks

sentry = Sentry(app, dsn='https://cc465b09e4004bd790db724a7d4252eb:6f73513a850d4e26b34612de0a08f7c9@192.168.20.244:9000//6')

# 初始化浏览器池子
from public.pool import PoolOptions,Pool
options = PoolOptions()
pool = Pool(options)


@app.route('/task', methods=['post'])
def export_task():

    # 企业号码，账号，密码，
    data = request.json or {}
    res = {}
    site = ''
    login_info = {}
    ztList = []
    callback_ip = ''
    if not data:
        if not request.form:
            res['msg'] = '没有数据'
        else:
            site = request.form.get('db_name', '')
            login_info = request.form.get('login_info', '')
            callback_ip = request.form.get('callback_ip', '')
            login_info = json.loads(login_info)
            zt = request.form.get('zt', '')
            ztList = json.loads(zt)
    else:
        site = data.get('db_name', '')
        login_info = data.get('login_info', '')
        callback_ip = request.form.get('callback_ip', '')
        ztList = data.get('zt', '')

    if site == 'kungeek':

        browser = pool.get_browser('chrome', 'kungeek')
        msg = try_to_login(browser,login_info,'HSZ')

        if msg == '登陆成功':
            from huisuanzhang.NewViews import GetInfo
            gti = GetInfo(browser)
            ztData = gti.getAllzt()
            pool.close_browser(browser)

            export_tasks(login_info, ztList, site, callback_ip, queue='export_out_kungeek')

            # 开始任务
            # signature('export_out_kungeek', args=(login_info, ztList, site, callback_ip), app=celery_app).apply_async(queue='export_in')

            res['id'] = str(id)
            res['msg'] = 'ok'
            res['zt'] = [item['name'].strip() for item in ztData]

        else:
            res['msg'] = msg

    elif site == '17DZ':

        browser = pool.get_browser('chrome', 'yiqidai')
        msg = try_to_login(browser,login_info,'17DZ')

        if msg == '登陆成功':
            from yiqidai.NewViews import GetInfo
            dz = GetInfo(browser)
            ztData = dz.getAllzt()
            pool.close_browser(browser)

            export_tasks(login_info, ztList, site, callback_ip,queue='export_out_yiqidai')

            # 开始任务
            # signature('export_out_yiqidai', args=(login_info, ztList, site, callback_ip), app=celery_app).apply_async(queue='export_in')

            res['msg'] = 'ok'
            res['zt'] = [item['customerFullName'].strip() for item in ztData]
        else:
            res['msg'] = msg

    elif site == 'yunzhangfang':

        browser = pool.get_browser('chrome', 'yunzhangfang')
        msg = try_to_login(browser,login_info,'YZF')

        if msg == '登陆成功':
            from yunzhangfang.NewViews import GetInfo
            yzf = GetInfo(browser)
            ztData = yzf.getAllzt()
            pool.close_browser(browser)

            export_tasks(login_info, ztList, site, callback_ip, queue='export_out_yunzhangfang')

            # 开始任务
            # signature('export_out_yunzhangfang', args=(login_info, ztList, site, callback_ip),app=celery_app).apply_async(queue='export_in')

            res['msg'] = 'ok'
            res['zt'] = [item['qymc'].strip() for item in ztData]
        else:
            res['msg'] = msg

    elif site == 'datawisee':
        browser = pool.get_browser('chrome', 'datawisee')
        msg = try_to_login(browser,login_info,'QMX')

        if msg == '登陆成功':
            from yunzhangfang.NewViews import GetInfo
            yzf = GetInfo(browser)
            ztData = yzf.getAllzt()
            pool.close_browser(browser)

            export_tasks(login_info, ztList, site, callback_ip, queue='export_out_datawisee')

            # 开始任务
            # signature('export_out_datawisee', args=(login_info, ztList, site, callback_ip), app=celery_app).apply_async(queue='export_in')

            res['msg'] = 'ok'
            res['zt'] = [item['qymc'].strip() for item in ztData]
        else:
            res['msg'] = msg

    return jsonify(res)


def try_to_login(browser,login_info,zdhm):
    getInfo = None
    if zdhm == 'HSZ':
        from huisuanzhang.NewViews import GetInfo
        getInfo = GetInfo(browser)
    elif zdhm == '17DZ':
        from yiqidai.NewViews import GetInfo
        getInfo = GetInfo(browser)
    elif zdhm == 'YZF':
        from yunzhangfang.NewViews import GetInfo
        getInfo = GetInfo(browser)

    # 登陆
    i = 1
    while True:
        msg = getInfo.login(login_info)
        if msg == '登陆成功':
            return msg
        elif msg == '登录失败':
            i += 1
            continue
        elif msg == '账号和密码不匹配,请重新输入':
            return msg
        elif msg == '账号已停用或合同未审核通过':
            return msg
        elif msg == '账号不存在或已停用':
            return msg
        elif i > 4:
            return '验证码错误%s次,需要人工介入' % i
        elif msg == '验证码错误,请重新输入':
            i += 1
            continue


if __name__ == '__main__':
    # app.run(host='0.0.0.0',debug=True,processes=4)
    app.run(host='0.0.0.0',port=5500,debug=False,threaded=False)
    # 设置threaded为True，开启的多线程是指不同路由使用多线程来处理请求，不是指单个路由多线程处理请求
