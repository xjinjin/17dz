# -*- coding:utf-8 -*-

from task.tasks import *

def export_tasks(login_info, ztList, site, callback_ip,queue='export_out_yiqidai'):


    if queue == 'export_out_yiqidai':

        res = taskExport_yiqidai_out.apply_async(args=[login_info,ztList,site,callback_ip], retry=True, queue=queue, immutable=True)

    elif queue == 'export_out_kungeek':
        res = taskExport_kungeek_out.apply_async(args=[login_info,ztList,site,callback_ip], retry=True, queue=queue, immutable=True)

    elif queue == 'export_out_yunzhangfang':
        res = taskExport_yunzhangfang_out.apply_async(args=[login_info,ztList,site,callback_ip], retry=True, queue=queue, immutable=True)
