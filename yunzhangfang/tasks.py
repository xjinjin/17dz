# -*- coding: utf-8 -*-
import time

# from celery_tasks.main import celeryApp
from public.duboo_telnet import callBack
from manage import YZFMongoInit, pool

db = YZFMongoInit.db

from yunzhangfang.NewViews import GetInfo


@celery.task(name='yunzhangfang')
def taskExport():
    browser = pool.get_browser("chrome", 'YZF')
    getInfo = GetInfo(browser)

    # 从mongo里取任务
    all_tasks = db.task_msg.find({'status':'等待执行'})

    if not all_tasks:
        return '没有任务'

    for task in all_tasks:
        #取出数据
        setName = task['task_info']['login_info']['account']
        callback_ip = task['task_info']['callback_ip']
        info = task['task_info']['login_info']
        Allzts = task['task_info']['zt']
        db_name = task['task_info']['db_name']
        taskId = str(task['_id'])
        YZFMongoInit.account = setName

        #登陆
        i = 1
        while True:
            msg = getInfo.login(info)
            if msg == '登陆成功':
                YZFMongoInit.update_status(taskId,'登陆成功,开始导出')
                break
            elif msg == '账号和密码不匹配,请重新输入':
                YZFMongoInit.update_status(taskId, msg)
                return
            elif i>4:
                YZFMongoInit.update_status(taskId, msg)
                return '错误次数过多,需人工介入'
            elif msg == '验证码错误,请重新输入':
                YZFMongoInit.update_status(taskId, '验证码错误,第%s次尝试'%i)
                i+=1
                continue

        time.sleep(0.5)


        Zts = getInfo.getAllzt()
        if not Zts:
            msg = '获取所有账套信息失败'
            YZFMongoInit.update_status(taskId,msg)


        #保存所有的账套信息
        # YZFMongoInit.save_zts(Zts)

        for zt in Zts:
            currentKjnd = zt['currentKjnd']
            currentKjqj = zt['currentKjqj']
            qyid = zt['qyid']
            qymc = zt['qymc'].strip()

            #拼接url
            # getInfo.createUrl(currentKjnd,currentKjqj,qyid)

            if qymc not in Allzts: #判断是否在传递过来的账套里面
                continue

            #创建账套存储结构
            documentId = YZFMongoInit.create_set(qymc)

            #获取所有期间
            Qjlist,ztdm = getInfo.dates(qyid, currentKjnd, qymc)
            time.sleep(0.5)

            #企业信息
            try:
                getInfo.company_info(qyid,qymc)
            except Exception as e:
                msg = '获取企业信息失败:%s'%str(e)
                YZFMongoInit.update_status(taskId,msg)
            else:
                msg = '企业信息导出成功'
                YZFMongoInit.update_status(taskId, msg)
            time.sleep(0.5)

            #会计科目
            try:
                msg = getInfo.kjkm(ztdm,qyid,qymc,currentKjnd,currentKjqj)
            except Exception as e:
                msg = '获取会计科目失败:%s'%str(e)
                YZFMongoInit.update_status(taskId, msg)
            else:
                YZFMongoInit.update_status(taskId, msg)
            time.sleep(0.5)

            #凭证
            try:
                msg = getInfo.voucher(Qjlist,ztdm,qymc)
            except Exception as e:
                msg = '获取凭证失败:%s'%str(e)
                YZFMongoInit.update_status(taskId, msg)
            else:
                YZFMongoInit.update_status(taskId, msg)

            time.sleep(0.5)

            #币别列表
            Bilist = getInfo.bibie(ztdm)
            time.sleep(0.5)

            #科目余额
            try:
                msg = getInfo.kmye(Qjlist,ztdm,qyid,qymc,Bilist)
            except Exception as e:
                msg = '获取科目余额失败:%s'%str(e)
                YZFMongoInit.update_status(taskId, msg)
            else:
                YZFMongoInit.update_status(taskId, msg)
            time.sleep(0.5)

            #获取数量金额科目余额表
            try:
               getInfo.sljeye(Qjlist,ztdm,qyid,qymc,Bilist)
            except Exception as e:
                msg = '获取数量金额科目余额表失败:%s'%str(e)
                YZFMongoInit.update_status(taskId, msg)
            else:
                YZFMongoInit.update_status(taskId, msg)

            # 记录一个账套导出成功
            msg = '%s 导出完成' % qymc
            try:
                YZFMongoInit.update_status(taskId, msg)
            except Exception as e:
                raise e

            # 进行回调 回调参数：db_name,collection,_id
            colletionId = 'm_' + info['account']
            if not callback_ip:
                callback_host = ''
                callback_port = ''
            else:
                callback_host = callback_ip[:14]
                callback_port = callback_ip[15:]

            resp = callBack(db_name, colletionId, documentId,callback_host,callback_port)


        #任务完成后，向数据库存入任务完成的消息
        pool.close_browser(browser)
        try:
            YZFMongoInit.task_finished(taskId)
        except Exception as e:
            return '更新任务完成时间失败:%s'%str(e)
        finally:
            res = '任务完成'
            return res



if __name__ == '__main__':
    taskExport()