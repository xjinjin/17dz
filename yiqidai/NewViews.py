# -*- coding: utf-8 -*-
import datetime
import json
import time
from flask import jsonify
from splinter.browser import Browser

class GetInfo():
    conn = ''
    browser = ''

    def __init__(self,browser,conn=None,to_sql=None):

        # 数据库存储初始化 表名称、登陆用户名
        self.exportSql = to_sql

        if browser:
            self.browser = browser
            self.conn = conn
        else:
            try:
                self.browser = Browser("chrome", headless=False)
                self.browser.driver.set_window_size(1600, 1000)
            except Exception as e:
                self.browser = None

    # 登陆
    def login(self, info):
        # 账号，密码，
        account = info.get('account')
        password = info.get('password')

        if self.browser.url == 'https://17dz.com/manage/index.html':
            if account == self.loginName():
                return '登陆成功'

        self.browser.visit('https://17dz.com/home/login.html')

        # 校验是否为空
        if not all([account, password]):
            return jsonify(errmsg='参数不全')

        with self.browser.get_iframe('loginIframe') as iframe:
            iframe.find_by_css('input[id="id__0"]').first.fill(account)
            iframe.find_by_css('input[id="id__1"]').first.fill(password)
            iframe.find_by_text('登录').first.click()

        time.sleep(2)

        if self.browser.url == 'https://17dz.com/manage/index.html':
            return '登陆成功'
        else:
            return '账号和密码不匹配,请重新输入'


    def loginName(self):
        js = '''getloginName=function(){

                $.ajax({
                    type:'GET',
                    url: 'https://17dz.com/xqy-portal-web/manage/login/getLoginSession?_=1544003601263',
                    contentType:'application/json;charset=utf-8',
                    success: function (result) {
                        if(result.success) {
                            top.Id = result;
                        } else {
                            top.Id = result;
                        }
                    }
                })
            }'''

        self.browser.evaluate_script(js)
        self.browser.evaluate_script('getloginName()')
        i = 1
        loginName = ''
        while True:
            if self.browser.evaluate_script("top.Id"):
                loginName = self.browser.evaluate_script('top.Id').get('body').get('loginName')
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass
        self.browser.evaluate_script('top.Id=""')

        return loginName


    # 登陆成功后获取账套列表
    def getAllzt(self):

        # self.browser.find_by_text('凭证查看').first.click()
        import datetime
        d = datetime.datetime.now()
        period = datetime.date(d.year - (d.month == 1), d.month - 1 or 12, 1).strftime('%Y')

        js = '''getCustomerId=function(){
                var data = {customerName:"", pageNo:1 , pageSize:"500" , searchType:"ALL"}
                $.ajax({
                    type:'POST',
                    url: 'https://17dz.com/xqy-portal-web/manage/customer/queryCustomers',
                    contentType:'application/json;charset=utf-8',
                    data : JSON.stringify(data),
                    success: function (result) {
                        if(result.success) {
                            top.customerId = result;
                        } else {
                            top.customerId = result;
                        }
                    }
                })
            }
            '''


        new_js = '''getCustomerId=function(period){
                    var data = {"pageNo":1,
                                "pageSize":"500",
                                "period":period,
                                "customerNoOrNameLike":"",
                                "accountCloseStatus":"",
                                "sortField":"",
                                "sortDirection":false
                        }
                    $.ajax({
                        type:'POST',
                        url: 'https://17dz.com/xqy-portal-web/manage/finance/queryCustomer',
                        contentType:'application/json;charset=utf-8',
                        data : JSON.stringify(data),
                        success: function (result) {
                            if(result.success) {
                                top.customerId = result;
                            } else {
                                top.customerId = result;
                            }
                        }
                    })
                }'''


        self.browser.evaluate_script(new_js)

        self.browser.evaluate_script('getCustomerId("%s")'%period)
        i = 1
        Id = []
        while True:
            if self.browser.evaluate_script("top.customerId"):
                Id = self.browser.evaluate_script('top.customerId')['body']['list']
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass
        self.browser.evaluate_script('top.customerId=""')

        customerId = Id[0]['customerId']

        js2 = '''getAllzt=function(customerId){
                var data = {key: "", customerId: customerId}
                $.ajax({
                    type:'POST',
                    url: 'https://17dz.com/xqy-portal-web/manage/workbench/getAccountCustomers',
                    contentType:'application/json;charset=utf-8',
                    data : JSON.stringify(data),
                    success: function (result) {
                        if(result.success) {
                            top.zt_data = result;
                        } else {
                            top.zt_data = result;
                        }
                    }
                })
            }'''

        self.browser.evaluate_script(js2)

        self.browser.evaluate_script('getAllzt("%s")'%customerId)
        i = 1
        ztData = {}
        while True:
            if self.browser.evaluate_script("top.zt_data"):
                ztData = self.browser.evaluate_script('top.zt_data').get('body','')
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass
        self.browser.evaluate_script('top.zt_data=""')

        return ztData


    # 切换账套,得到账套的起始和结束日期
    def switchZt(self, params):

        customerId = params['customerId']
        accountSetId = params['accountSetId']
        customerName = params['customerName']
        customerShortName = params['customerShortName']
        # getKhxx('127059881','4320800','上海路卡服装有限公司','上海路卡服装有限公司')
        js = '''getKhxx=function(customerId,accountSetId,customerName,customerShortName){
                $.ajax({
                    type:'PUT',
                    url:'https://17dz.com/xqy-portal-web/finance/account/session/accountSet',
                    data : {customerId:customerId,accountSetId:accountSetId,customerName:customerName,customerShortName:customerShortName,platform:'yqdz'},
                    dataType: 'json',
                    success: function (result) {
                        if(result.success) {
                            top.khxx = result;
                        } else {
                            top.khxx = result;
                        }
                    }
                })
            }'''

        self.browser.evaluate_script(js)

        self.browser.evaluate_script('getKhxx("%s","%s","%s","%s")' % (customerId,accountSetId,customerName,customerShortName))
        i = 1
        khxx = {}
        while True:
            if self.browser.evaluate_script("top.khxx"):
                khxx = self.browser.evaluate_script('top.khxx')
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass
        self.browser.evaluate_script('top.khxx=""')
        try:
            startQj = khxx.get('body').get('createPeriod')
            endQj = khxx.get('body').get('lastPeriod')
        except Exception as e:
            return '网络异常，请稍后重试'

        dateStart = datetime.datetime.strptime(startQj, '%Y%m')
        dateEnd = datetime.datetime.strptime(endQj, '%Y%m')

        dates = []
        dates.append(dateStart.strftime('%Y%m'))
        while dateStart <= dateEnd:
            dateStart += datetime.timedelta(weeks=4)
            dates.append(dateStart.strftime('%Y%m'))

        datesList = sorted(list(set(dates)))

        return datesList


    # 凭证
    def voucher(self, QjList, ztID, infoname):

        js = '''get_Voucher=function(kjqj_date){
                var data = {"beginPeriod":kjqj_date,
                            "endPeriod":kjqj_date,
                            "titleCode":"",
                            "beginNumber":"",
                            "endNumber":"",
                            "beginMoney":"",
                            "endMoney":"",
                            "summary":"",
                            "pageSize":"1000",
                            "pageNo":0
                }
                $.ajax({
                    type: "POST",
                    url: 'https://17dz.com/xqy-portal-web/finance/accDocs/list',
                    contentType:'application/json;charset=utf-8',
                    data: JSON.stringify(data),
                    success: function (result) {
                        if(result.success) {
                            top.voucher_data = result;
                        } else {
                            top.voucher_data = result;
                        }
                    }
                })
            }
            '''
        self.browser.evaluate_script(js)
        #创建数据库的infonameID
        infonameID = self.exportSql.init_infoname(infoname).id
        try:
            for Qj in QjList:

                self.browser.evaluate_script('get_Voucher("%s")' %Qj)
                i = 1
                voucher_data = {}
                while True:
                    if self.browser.evaluate_script("top.voucher_data"):
                        data = self.browser.evaluate_script('top.voucher_data')
                        if data:
                            voucher_data = data.get('body')

                        break
                    elif i > 5:
                        break
                    else:
                        time.sleep(0.5)
                        i += 1
                        pass
                self.browser.evaluate_script('top.voucher_data=""')

                voucherString = json.dumps(voucher_data)

                # 保存到数据库
                self.exportSql.insert_new(ztID, Qj, infonameID, voucherString)
        except Exception as e:
            msg = '凭证导出失败：{}'.format(str(e))
        else:
            msg = '凭证导出成功'
        return msg

    # 科目余额表
    def kmsheet(self, QjList, ztID, infoname,):

        # 创建数据库的infonameID
        infonameID = self.exportSql.init_infoname(infoname).id
        try:
            for Qj in QjList:
                #获取科目余额
                km_data = self.getKMBody(Qj)

                '''第一版
                # #获取数量金额式
                # slje_data = self.getKMBody(Qj,"B,S")
                # #获取外币金额式
                # wbje_data = self.getKMBody(Qj,"B,W")
                # li = {}
                # li['kmye'] = km_data
                # li['slje'] = slje_data
                # li['wbje'] = wbje_data'''

                # 保存到数据库
                kmString = json.dumps(km_data)
                self.exportSql.insert_new(ztID,Qj,infonameID,kmString)

        except Exception as e:
            msg = '科目余额导出失败：{}'.format(str(e))
        else:
            msg = '科目余额导出成功'
        return msg


    def getKMBody(self,Qj):
        js = '''getKMBody=function(kjqj_date){
                        var data = {
                            "beginPeriod":kjqj_date,
                            "endPeriod":kjqj_date,
                            "beginTitleCode":"",
                            "endTitleCode":"",
                            "pageNo":0,
                            "pageSize":5000,
                            "showYearAccumulated":true,
                            "assistantId":"",
                            "assistantType":"",
                            "showAssistant":true,
                            "titleLevel":6,
                            "showEndBalance0":true,
                            "showQuantity":false,
                            "fcurCode":""
                            }
                        $.ajax({
                            type: "POST",
                            url: 'https://17dz.com/xqy-portal-web/finance/accountBalanceSheet/query',
                            contentType:'application/json;charset=utf-8',
                            data: JSON.stringify(data),
                            success: function (result) {
                                if(result.success) {
                                    top.KMBody = result;
                                } else {
                                    top.KMBody = result;
                                }
                            }
                        })
                    }
                    '''
        self.browser.evaluate_script(js)

        # 获取科目余额
        self.browser.evaluate_script('getKMBody("%s")' % Qj)
        data_km = {}
        i = 1
        while True:
            if self.browser.evaluate_script("top.KMBody"):
                data_km = self.browser.evaluate_script('top.KMBody')['body']
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass
        self.browser.evaluate_script('top.KMBody=""')

        if Qj == "201601":
            print(data_km)

        return data_km


    # 辅助核算余额表  说明：
    def fzhssheet(self, QjList, company):

        js = '''getFzhssheet=function(kjqj_date){
                var data = {
                    "assistantType":"c",
                    "beginCode":"",
                    "endCode":"",
                    "beginPeriod":kjqj_date,
                    "endPeriod":kjqj_date,
                    "assistantId":"",
                    "bwsTypeList":"B",
                    "level":"6",
                    "showEmptyBalance":false,
                    "firstAccountTitle":false,
                    "accumulated":true
                }
                $.ajax({
                    type: "POST",
                    url: 'https://17dz.com/xqy-portal-web/finance/assistantBalanceBook/list',
                    contentType:'application/json;charset=utf-8',
                    data: JSON.stringify(data),
                    success: function (result) {
                        if(result.success) {
                            top.fzhs_data = result;
                        } else {
                            top.fzhs_data = result;
                        }
                    }
                })
            }'''

        self.browser.evaluate_script(js)

        fzhs_dict = {}

        for Qj in QjList:

            self.browser.evaluate_script('getFzhssheet("%s")' % Qj)
            i = 1
            while True:
                if self.browser.evaluate_script("top.fzhs_data"):
                    fzhsye = self.browser.evaluate_script('top.fzhs_data')['body']
                    break
                elif i > 5:
                    break
                else:
                    time.sleep(0.5)
                    i += 1
                    pass
            self.browser.evaluate_script('top.fzhs_data=""')

            slje = self.getFZBody(Qj,"s","B,S")
            wbje = self.getFZBody(Qj,"w","B,W")

            li = {}
            li['fzhsye'] = fzhsye
            li['slje'] = slje
            li['wbje'] = wbje

            fzhs_dict[str(Qj)] = li

        if not fzhs_dict:
            return '获取辅助核算余额表失败'

        # 保存到数据库
        try:
            self.exportSql.update_fzsheet(company, fzhs_dict)
        except Exception as e:
            return '辅助核算余额表保存失败:%s' % e

        return '辅助核算余额表导出成功'

    def getFZBody(self,Qj,balanceType,bwsTypeList):
        js = '''getFZBody=function(kjqj_date,balanceType,bwsTypeList){
                var data = {"beginPeriod":"201811",
                            "endPeriod":"201811",
                            "beginCode":"",
                            "endCode":"",
                            "assistantType":"c",
                            "assistantId":"",
                            "balanceType":balanceType,
                            "ifCondition":false,
                            "bwsTypeList":bwsTypeList,
                            "firstAccountTitle":false,
                            "showEmptyBalance":false,
                            "level":"6",
                            "accumulated":true
                }
                $.ajax({
                    type: "POST",
                    url: 'https://17dz.com/xqy-portal-web/finance/assistantBalanceBook/list',
                    contentType:'application/json;charset=utf-8',
                    data: JSON.stringify(data),
                    success: function (result) {
                        if(result.success) {
                            top.FZBody = result;
                        } else {
                            top.FZBody = result;
                        }
                    }
                })
            }'''

        self.browser.evaluate_script(js)

        # 获取科目余额
        self.browser.evaluate_script('getFZBody("%s","%s","%s")' % (Qj, balanceType, bwsTypeList))

        i = 1
        km_data = {}
        while True:
            if self.browser.evaluate_script("top.FZBody"):
                km_data = self.browser.evaluate_script('top.FZBody')['body']
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass
        self.browser.evaluate_script('top.FZBody=""')

        return km_data


    #现金流量
    def xjll(self,QjList, ztID, infoname):

        jd_js = '''xjll=function(url){
                $.ajax({
                    type:'GET',
                    url: url,
                    success: function (result) {
                        if(result.success) {
                            top.xjll_data = result;
                        } else {
                            top.xjll_data = result;
                        }
                    }
                })
            }'''

        # self.browser.evaluate_script(xjll_js)

        self.browser.evaluate_script('window.open("about:blank")')
        self.browser.windows.current = self.browser.windows[1]

        #获取起始季度
        jd_url = 'https://17dz.com/xqy-portal-web/finance/cashFlowInitial/queryInitialPeriod?_=1547174631618'
        self.browser.visit(jd_url)
        jd_jsonStr = self.browser.find_by_tag('pre').first.text
        init_jd = json.loads(jd_jsonStr)

        #月报
        # 创建数据库的infonameID
        Y_infonameID = self.exportSql.init_infoname(infoname + '-月报').id
        try:
            for Qj in QjList:
                time.sleep(0.5)
                y_url = 'https://17dz.com/xqy-portal-web/finance/cashFlowSheet?accountPeriod={}&sheetType=2&_=1543301545878'.format(Qj)
                self.browser.visit(y_url)
                Y_jsonStr = self.browser.find_by_tag('pre').first.text

                #月报存库
                self.exportSql.insert_new(ztID,Qj,Y_infonameID,Y_jsonStr)
        except Exception as e:
            msg = '现金流量月报导出失败：{}'.format(str(e))
        else:
            msg =  '现金流量月报导出成功'


        #季报
        # 创建数据库的infonameID
        J_infonameID = self.exportSql.init_infoname(infoname + '-季报').id
        try:
            for Qj in QjList:
                year = Qj[:4]
                if Qj[4:] in ['01','02','03']:
                    jd = '1'
                elif Qj[4:] in ['04','05','06']:
                    jd = '2'
                elif Qj[4:] in ['07','08','09']:
                    jd = '3'
                elif Qj[4:] in ['10','11','12']:
                    jd = '4'
                time.sleep(0.5)
                j_url = 'https://17dz.com/xqy-portal-web/finance/cashFlowSheet/quarterlyReport?year={}&season={}&_=1543301545880'.format(year,jd)
                self.browser.visit(j_url)
                J_jsonStr = self.browser.find_by_tag('pre').first.text
                qj = '%s-%s' % (year, jd)
                # 季报存库
                self.exportSql.insert_new(ztID, qj, J_infonameID, J_jsonStr)
        except Exception as e:
            msg = '现金流量季报导出失败：{}'.format(str(e))
        else:
            msg =  '现金流量季报导出成功'

        self.browser.windows.current.close()
        self.browser.windows.current = self.browser.windows[0]

        return msg

    # 基础设置
    def settings(self, customerId, ztID,accountSetId,QjList,infoname):
        set_js = '''getSettings=function(url){
                        $.ajax({
                            type:'GET',
                            url: url,
                            success: function (result) {
                                if(result.success) {
                                    top.load_data = result;
                                } else {
                                    top.load_data = result;
                                }
                            }
                        })
                    }'''
        self.browser.evaluate_script(set_js)

        #科目
        # 创建数据库的infonameID
        kmID = self.exportSql.init_infoname(infoname+'-科目').id
        km_dict = {}
        # 获取资产，负债，权益，成本，损益对应的编码
        code_url = 'https://17dz.com/xqy-portal-web/finance/accountTitle/types?systemAccountId=1&_=1542955356592'
        AllCodes = self.get_settings(code_url).get('body',[])
        for i in AllCodes:
            code = i['code']
            name = i['name']
            km_url = 'https://17dz.com/xqy-portal-web/finance/customerAccountTitles/' \
                  'listByType?customerId={}&subjectType={}&_=1542955356593'.format(customerId,code)
            res = self.get_settings(km_url)
            km_dict[name] = res

        #辅助核算
        # 创建数据库的infonameID
        fzID = self.exportSql.init_infoname(infoname+'-辅助核算').id
        fz_dict = {}
        Base_url = 'https://17dz.com/xqy-portal-web/finance/{}/list' \
                '/page?key=&accountSetId={}&customerId={}&pageNo=0&pageSize=10000'

        FZ_List = ['clients','suppliers','inventories','projects']

        for name in FZ_List:
            newUrl = Base_url.format(name,accountSetId,customerId)
            data = self.get_settings(newUrl).get('body')
            fz_dict[name] = data

        # 币别
        # 创建数据库的infonameID
        bbID = self.exportSql.init_infoname(infoname+ '-币别').id
        url = 'https://17dz.com/xqy-portal-web/finance/exchangeRates/all?accountPeriod={}&_=1542955356686'
        for Qj in QjList:
            newurl = url.format(Qj)
            B = self.get_settings(newurl)
            # 将币别存库
            self.exportSql.insert_new(ztID, Qj, bbID , json.dumps(B))

        try:
            # 将科目存库
            self.exportSql.insert_new(ztID, '',kmID,json.dumps(km_dict))
            # 辅助核算保存入库
            self.exportSql.insert_new(ztID, '',fzID,json.dumps(fz_dict))

        except Exception as e:
            return '基础设置导出成功保存失败:{}'.format(str(e))

        return '基础设置导出成功'


    def get_settings(self, url):

        try:

            self.browser.evaluate_script('getSettings("%s")' % url)

        except Exception as e:
            print(e)
        i = 1
        settings_data = {}
        while True:
            if self.browser.evaluate_script("top.load_data"):
                settings_data = self.browser.evaluate_script('top.load_data')
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass

        self.browser.evaluate_script('top.load_data=""')

        return settings_data


    #获取现金流量
    def get_xjll(self, url):

        try:
            self.browser.evaluate_script('xjll("%s")' % url)
            time.sleep(5.5)
        except Exception as e:
            print(e)
        i = 1
        xjll_data = {}
        while True:
            if self.browser.evaluate_script("top.xjll_data"):
                xjll_data = self.browser.evaluate_script('top.xjll_data')
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass

        self.browser.evaluate_script('top.xjll_data=""')

        return xjll_data
