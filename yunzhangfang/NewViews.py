# -*- coding:utf-8 -*-
import datetime
import json
import time

from yunzhangfang.downloader import Chrome


class GetInfo():

    def __init__(self,browser,to_sql=None,sentry=None):
        self.down = Chrome(browser)
        self._sentry = sentry
        # 数据库存储初始化 表名称、登陆用户名
        self.exportSql = to_sql

    def login(self,login_info):
        if self.down.browser.url == 'http://daizhang.yunzhangfang.com/static/index/index.html':
            return '登陆成功'
        i = 1
        while True:
            try:
                # down.down('http://daizhang.yunzhangfang.com/static/index/index.html')
                self.down.down('http://sso.yunzhangfang.com/login.html?timestamp=1543366016919&url=http%3A%2F%2Fdaizhang.yunzhangfang.com%2F')
            except Exception as e:
                if i > 3:
                    return '访问受限'
                else:
                    continue
            else:
                break

        time.sleep(0.2)

        '''登陆界面'''
        # 获取账号输入标签
        # 账号，密码，
        account = login_info.get('account')
        password = login_info.get('password')

        if not all([account, password]):
            return '参数不全'


        #填写用户名密码
        form = self.down.browser.find_by_css('form[id="loginFrom"]').first
        form.find_by_css('input[name="userName"]').first.fill(account)
        form.find_by_css('input[name="password"]').first.fill(password)

        try:
            self.down.browser.find_by_css('input[id="login_id"]').first.click()
        except Exception as e:
            return '登录失败'

        if self.down.browser.url == 'http://daizhang.yunzhangfang.com/static/index/index.html':
            return '登陆成功'
        else:
            return '账号和密码不匹配,请重新输入'

        # username = 'dcg'
        # password = 'hz123456'

    #获取所有的账套信息
    def getAllzt(self):
        '''获取企业'''

        with self.down.browser.get_iframe('indexIframe') as iframe:
            params = iframe.evaluate_script('''$.extend({
                pageSize: 2000,
                currentKjnd: thisPage.Echarts.dataTime.date.getFullYear(),
                currentKjqj: thisPage.Echarts.dataTime.date.getMonth()+1
                },thisPage.DataGrid.pager.param)''')

        js = '''script=function(username, password,kjnd,kjqj,qyid,ztdm,bzid){
                param=%s,

                Utils.ajax.loadingAjax({
                    url:'/portal/api/index/ajax/homeQyListByCondition',
                    data:param,
                    success:function(result){
                        window.res=result;
                    }});
                }'''
        page = 1
        allZts = []
        import json

        while True:
            params['page'] = page
            zts = self.down.evaluate(js%json.dumps(params))
            allZts += zts
            #判断是否有下一页
            if len(zts) < 2000:
                return allZts
            else:
                page += 1
                continue

    '''def createUrl(self,currentKjnd,currentKjqj,qyid):

        # baseurl = 'http://daizhang.yunzhangfang.com'
        #
        # geturl = self.down.browser.evaluate_script("YZF.Public.versionUrl('/static/index/company.html?qyid='+%s+'&kjnd='+%s+'&kjqj='+%s)"%(qyid,currentKjnd,currentKjqj))
        # print("YZF.Public.versionUrl('/static/index/company.html?qyid='+%s+'&kjnd='+%s+'&kjqj='+%s)"%(qyid,currentKjnd,currentKjqj))
        # URL = baseurl+geturl
        #
        # # self.down.browser.evaluate_script("window.location='%s'"%URL)
        # down.browser.visit(URL)

        with self.down.browser.get_iframe('indexIframe') as iframe:
            iframe.evaluate_script('openCompany("%s")'% qyid)'''


    #切换进账套页面
    # def getIntoUrl(self):
    #     pass

    #获取期间
    def dates(self,qyid, kjnd, qymc):
        '''获取最新一期'''
        js = '''get_Qj=function(){
                $.ajax({
                    type: "GET",
                    url: 'http://daizhang.yunzhangfang.com/portal/api/index/ajax/main?qyid=%s',
                    dataType: "json",
                    success: function (result) {
                        if(result.success) {
                            top.Qj = result;
                        } else {
                            top.Qj = result;
                        }
                    }
                })
            }'''
        js2 = js%qyid
        self.down.browser.evaluate_script(js2)
        time.sleep(0.5)
        self.down.browser.evaluate_script('get_Qj()')
        time.sleep(0.5)
        res = self.down.browser.evaluate_script('top.Qj')
        startQj = res['result']['startTime']
        endQj = res['result']['endTime']
        ztdm = res['result']['ztdm']
        dateStart = datetime.datetime.strptime(startQj, '%Y%m')
        dateEnd = datetime.datetime.strptime(endQj, '%Y%m')

        dates = []
        while dateStart < dateEnd:
            dateStart += datetime.timedelta(weeks=4)
            dates.append(dateStart.strftime('%Y%m'))

        datesList = sorted(list(set(dates)))

        return datesList,ztdm


    def company_info(self,qyid, qymc,zt_id,infoname):
        '''获取企业信息'''
        Qj = ''
        try:
            # 获取基本信息
            js = '''script=function(username, password,kjnd,kjqj,qyid,ztdm,bzid){
                    url='/portal/api/customerManager/queryCompanyByQyid';
                    params={'qyid':qyid}
                        $.get(url, params, function(_data) {
                            if (_data.success) {
                            window.res=_data;}
                            });
                    }'''
            res = self.down.evaluate(js, qyid=qyid)
            res['limit'] = ''
            jbxx = json.dumps(res)
            infonameID = self.exportSql.init_infoname(infoname + '-基本信息').id
            self.exportSql.insert_new(zt_id, Qj, infonameID, jbxx)
            # 获取国税信息
            js = '''script=function(username, password,kjnd,kjqj,qyid,ztdm,bzid){
                    url='/portal/api/customerManager/queryGdsInfo';
                    params={'qyid':qyid,'gdsbz':1}
                        $.get(url, params, function(_data) {
                            if (_data.success) {
                            window.res=_data;}
                            });
                    }'''

            res = self.down.evaluate(js, qyid=qyid)
            res['limit'] = ''
            gsxx = json.dumps(res)
            infonameID = self.exportSql.init_infoname(infoname + '-国税信息').id
            self.exportSql.insert_new(zt_id, Qj, infonameID, gsxx)

            # 获取地税
            js = '''script=function(username, password,kjnd,kjqj,qyid,ztdm,bzid){
                    url='/portal/api/customerManager/queryGdsInfo';
                    params={'qyid':qyid,'gdsbz':2}
                        $.get(url, params, function(_data) {
                            if (_data.success) {
                            window.res=_data;}
                            });
                    }'''

            res = self.down.evaluate(js, qyid=qyid)
            res['limit'] = ''
            dsxx = json.dumps(res)
            # 创建数据库的infonameID
            infonameID = self.exportSql.init_infoname(infoname+'-地税信息').id
            # 保存到数据库
            self.exportSql.insert_new(zt_id, Qj, infonameID, dsxx)
        except Exception as e:
            if self._sentry:
                self._sentry.captureException()
            msg = infoname+'保存失败:{0}'.format(str(e))
        else:
            msg = infoname+'保存成功'
        return msg


    def kjkm(self,ztdm, qyid, qymc, currentKjnd,currentKjqj,zt_id,infoname):
        '''获取会计科目'''
        js = '''script=function(username, password,kjnd,kjqj,qyid,ztdm,bzid){
                Utils.ajax.postAjax({
                    url : '/system/api/system/ztkm/getAllZtkm',
                    data : {'ztdm':ztdm,'kjnd':kjnd,'kjqj':kjqj,'qyid':qyid,'bwbId':0},
                    success : function(result){
                    window.res=result;
                    }});
                }'''

        new_js = '''get_kjkm=function(){
                    var form = new FormData;
                    form.append("ztdm","zxj");
                    form.append("kjnd",123456);
                    form.append("kjqj",123456);
                    form.append("bwbId",0);
                    form.append("qyid",0);
                    $.ajax({
                        url: 'http://daizhang.yunzhangfang.com/system/api/system/ztkm/getAllZtkm',
                        type: "POST",
                        data: form,
                        processData:false,
                        contentType:false,
                        success: function (result) {
                            if(result) {
                                top.kjkm = result;
                            } else {
                                top.kjkm = result;
                            }
                        }
                    })
                }'''
        try:
            res = self.down.evaluate(js, ztdm=ztdm, qyid=qyid,kjnd=currentKjnd,kjqj=currentKjqj)
            res['limit'] = ''

            # 保存到数据库
            Qj = ''
            # 创建数据库的infonameID
            res_json = json.dumps(res)
            infonameID = self.exportSql.init_infoname(infoname).id
            self.exportSql.insert_new(zt_id, Qj, infonameID, res_json)
        except Exception as e:
            msg = '会计科目保存失败:{0}'.format(str(e))
        else:
            msg = '会计科目保存成功'

        return msg



    def bibie(self,ztdm):
        js = '''get_Bibie=function(){
                $.ajax({
                    type: "GET",
                    url: 'http://daizhang.yunzhangfang.com/system/api/fphl/getAllBzList?ztdm=%s',
                    dataType: "json",
                    success: function (result) {
                        if(result.success) {
                            top.bibie = result.result;
                        } else {
                            top.bibie = result.result;
                        }
                    }
                })
            }'''

        self.down.browser.evaluate_script(js%ztdm)
        time.sleep(0.5)
        self.down.browser.evaluate_script('get_Bibie()')
        time.sleep(0.5)
        res = self.down.browser.evaluate_script('top.bibie')
        b = {'kBzmc':'人民币','kBzid':0}
        res.insert(0,b)
        return res


    def sljeye(self, Qjlist, ztdm, qyid,Bilist,zt_id,infoname):
        '''获取数量金额科目余额表'''
        # jsUrl = '''String.prototype.format = function(){
        #                 var args = arguments;
        #                 return this.replace(/\{(\d+)\}/g,
        #                     function(m,i){
        #                         return args[i] || '';
        #                     });
        #                 }'''
        # self.down.browser.evaluate_script(jsUrl)
        # i = 1
        # while self.down.browser.evaluate_script('String.prototype.format==undefined'):
        #     time.sleep(0.5)
        #     i += 1
        #     if i > 5:
        #         break

        # js = '''sljeye=function(ztdm,kjnd,kjnd,kjqj,kjqj,kjqj,kBzid){
        #         var url = 'http://daizhang.yunzhangfang.com/pingzheng/api/zhangmu/slhs/getKmyeSlhs?ztdm={0}&startKjnd={1}&endKjnd={2}&kjqj={3}&qsyf={4}&jsyf={5}&qskm=&jskm=&qskmjc=&jskmjc=&sfxsfzhs=false&sfxswb=false&bzid={6}'
        #         if (String.prototype.format==undefined){
        #             url=url.replace(/\\{(\\d+)\\}/g,
        #             function(m,i){
        #                 return args[i] || '';
        #             })
        #         }
        #         else {
        #             url=url.format(ztdm,kjnd,kjnd,kjqj,kjqj,kjqj,kBzid)
        #         }
        #         $.ajax({
        #             type:# 'GET',
        #             url: url,
        #             success: function (result) {
        #                 if(result.success) {
        #                     top.sljeye = result;
        #                 } else {
        #                     top.sljeye = result;
        #                 }
        #             }
        #         })
        #     }'''

        new_js = '''sljeye=function(ztdm,kjnd,kjnd,kjqj,kjqj,kjqj,kBzid){
                    var params = {
                        'ztdm':ztdm,
                        'startKjnd':kjnd,
                        'endKjnd':kjnd,
                        'kjqj':kjqj,
                        'qsyf':kjqj,
                        'jsyf':kjqj,
                        'qskm':'',
                        'jskm':'',
                        'qskmjc':'',
                        'jskmjc':'',
                        'sfxsfzhs':false,
                        'sfxswb':false,
                        'bzid':kBzid
                    }
                    $.ajax({
                        type:'GET',
                        url: 'http://daizhang.yunzhangfang.com/pingzheng/api/zhangmu/slhs/getKmyeSlhs',
                        data: params,
                        dataType: "application/json",
                        success: function (result) {
                            if(result.success) {
                                top.sljeye = result;
                            } else {
                                top.sljeye = result;
                            }
                        }
                    })
                }'''

        # self.down.browser.evaluate_script(new_js)
        # time.sleep(2)
        from urllib.parse import urlencode
        sljeye_list = []
        try:
            for Qj in Qjlist:
                kjnd = Qj[:4]
                kjqj = Qj[4:]
                for i in Bilist:
                    sljeye_dict = {}
                    kBzid = str(i['kBzid'])
                    kBzmc = i['kBzmc']
                    # try:
                    #     self.down.browser.evaluate_script('sljeye(%s,%s,%s,%s,%s,%s,%s)'% (ztdm,kjnd,kjnd,kjqj,kjqj,kjqj,kBzid))
                    # except Exception as e:
                    #     msg = str(e)
                    # time.sleep(0.5)
                    # try:
                    #     res = self.down.browser.evaluate_script('top.sljeye')['result']
                    # except Exception as e:
                    #     msg = str(e)
                    # time.sleep(0.5)
                    time.sleep(0.5)
                    params = {
                        'ztdm': ztdm,
                        'startKjnd': kjnd,
                        'endKjnd': kjnd,
                        'kjqj': kjqj,
                        'qsyf': kjqj,
                        'jsyf': kjqj,
                        'qskm': '',
                        'jskm': '',
                        'qskmjc': '',
                        'jskmjc': '',
                        'sfxsfzhs': 'false',
                        'sfxswb': 'false',
                        'bzid': kBzid
                    }
                    data = urlencode(params)
                    Url = 'http://daizhang.yunzhangfang.com/pingzheng/api/zhangmu/slhs/getKmyeSlhs?'+data

                    for i in range(6):
                        if i == 5:
                            msg='获取数据失败'
                            return msg
                        try:
                            self.down.browser.visit(Url)
                        except Exception as e:
                            continue
                        else:
                            break

                    jsonString = self.down.browser.find_by_tag('pre').first.text
                    data = json.loads(jsonString)
                    result = data['result']
                    for i in sljeye_list:
                        if result in i.values():
                            result = 'null'
                    sljeye_dict['data'] = result
                    sljeye_dict['kjqj'] = str(Qj)
                    sljeye_dict['bibie'] = kBzmc
                    sljeye_list.append(sljeye_dict)

                    # 创建数据库的infonameID
                    infonameID = self.exportSql.init_infoname(infoname + '-' + kBzmc).id
                    self.exportSql.insert_new(zt_id, str(Qj), infonameID, result)

            #返回首页
            self.down.browser.visit('http://daizhang.yunzhangfang.com/static/index/index.html')

        # try:
        #     # 更改存储结构，币别>期间>data
        #     sljeye = {}
        #     for slj in sljeye_list:
        #         if slj['bibie'] in sljeye:
        #             # 创建数据库的infonameID
        #             infonameID = self.exportSql.init_infoname(infoname + '-' + slj.get('bibie')).id
        #             Qj = slj.get('kjqj')
        #             Data = slj.get('data')
        #             json_data = json.dumps(Data)
        #             self.exportSql.insert_new(zt_id, Qj, infonameID, json_data)
        #         else:
        #             sljeye[slj['bibie']] = {slj['kjqj']: slj['data']}

        except Exception as e:
            msg = '数量金额保存失败:'+str(e)
        else:
            msg = '数量金额保存成功'

        return msg


    def kmye(self,Qjlist,ztdm, qyid, Bilist, zt_id, infoname):
        '''获取科目余额'''
        jsUrl = '''String.prototype.format = function(){
                var args = arguments;
                return this.replace(/\{(\d+)\}/g,
                    function(m,i){
                        return args[i] || '';
                    });
                }'''
        self.down.browser.evaluate_script(jsUrl)
        i=1
        while self.down.browser.evaluate_script('String.prototype.format==undefined'):
            time.sleep(0.5)
            i += 1
            if i > 5:
                break

        js = '''kmye=function(kBzid,kjnd,ztdm,kjqj,kjqj,kjqj,kjnd,kjnd,kjqj,kjqj){
                var url = 'http://daizhang.yunzhangfang.com/pingzheng/api/zhangmu/listKemuYeM?qskm=&jskm=&qskmjc=1&jskmjc=4&sfxsfzhs=false&bzid={0}&kjnd={1}&ztdm={2}&kjqj={3}&qsyf={4}&jsyf={5}&startKjnd={6}&endKjnd={7}&sfxswb=true&qskmmc=&jskmmc=&startKjqj={8}&endKjqj={9}'
                if (String.prototype.format==undefined){
                    url=url.replace(/\\{(\\d+)\\}/g,
                    function(m,i){
                        return args[i] || '';
                    })
                }
                else {
                    url=url.format(kBzid,kjnd,ztdm,kjqj,kjqj,kjqj,kjnd,kjnd,kjqj,kjqj)
                }
                $.ajax({
                    type:'GET',
                    url: url,
                    success: function (result) {
                        if(result.success) {
                            top.kmye = result;
                        } else {
                            top.kmye = result;
                        }
                    }
                })
            }'''

        js2 = '''script=function(username,password,kjnd,kjqj,qyid,ztdm,bzid){
                url='/pingzheng/api/zhangmu/listKemuYe';
                params={'jskmjc':4,'sfxswb':'false','bzid':bzid,'qyid':qyid,'bwbId':0,'kjqj':kjqj,'kjnd':kjnd,'ztdm':ztdm}
                $.get(url, params, function(_data) {
                if (_data.success) {
                    window.res=_data;}
                });
            }'''


        self.down.browser.evaluate_script(js)
        time.sleep(2)

        km_list = []
        try:
            for Qj in Qjlist:
                kjnd = Qj[:4]
                kjqj = Qj[4:]
                for i in Bilist:
                    km_dict = {}
                    kBzid = str(i['kBzid'])
                    kBzmc = i['kBzmc']
                    if kBzmc == '人民币':
                        continue

                    time.sleep(0.5)
                    try:
                        self.down.browser.evaluate_script('kmye("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'%(kBzid,kjnd,ztdm,kjqj,kjqj,kjqj,kjnd,kjnd,kjqj,kjqj))
                    except Exception as e:
                        msg = str(e)

                    time.sleep(0.5)
                    try:
                        res = self.down.browser.evaluate_script('top.kmye')['result']['result']['data']
                    except Exception as e:
                        msg = str(e)

                    #判断是否有重复数据
                    for i in km_list:
                        if res in i.values():
                            res = 'null'
                    km_dict['data'] = res
                    km_dict['kjqj'] = str(Qj)
                    km_dict['bibie'] = kBzmc
                    km_list.append(km_dict)

                    # 创建数据库的infonameID
                    res_json = json.dumps(res)
                    infonameID = self.exportSql.init_infoname(infoname + '-' + kBzmc).id
                    self.exportSql.insert_new(zt_id, str(Qj), infonameID, res_json)

            for Qj in Qjlist:
                #单独抓取人民币
                kjnd = Qj[:4]
                kjqj = Qj[4:]
                new_dict = {}
                time.sleep(0.5)
                rmb_data = self.down.evaluate(js2, qyid=qyid, kjnd=kjnd, kjqj=kjqj, ztdm=ztdm, bzid=0)['result']['result']['data']
                time.sleep(0.5)

                # 判断是否有重复数据
                for i in km_list:
                    if rmb_data in i.values():
                        rmb_data = 'null'

                new_dict['data'] = rmb_data
                new_dict['kjqj'] = str(Qj)
                new_dict['bibie'] = '人民币'
                km_list.append(new_dict)

                # 创建数据库的infonameID
                rmb_data_json = json.dumps(rmb_data)
                infonameID = self.exportSql.init_infoname(infoname + '-' + '人民币').id
                self.exportSql.insert_new(zt_id, str(Qj), infonameID, rmb_data_json)

        # time.sleep(0.5)
        # try:
        #     # 更改存储结构，币别>期间>data
        #     kmye = {}
        #     for km in km_list:
        #         if km['bibie'] in kmye:
        #             # 创建数据库的infonameID
        #             infonameID = self.exportSql.init_infoname(infoname+'-'+km.get('bibie')).id
        #             Qj = km.get('kjqj')
        #             Data = km.get('data')
        #             String = json.dumps(Data)
        #             self.exportSql.insert_new(zt_id, Qj, infonameID, String)
        #         else:
        #             kmye[km['bibie']] = {km['kjqj']:km['data']}

        except Exception as e:
            msg = '科目余额保存失败：{}'.format(str(e))
        else:
            msg = '科目余额保存成功'

        return msg


    def voucher(self,Qjlist, ztdm, zt_id,infoname):
        """获取凭证"""
        js = '''script=function(username, password,kjnd,kjqj,qyid,ztdm,bzid){
                Utils.ajax.loadingAjax({
                url: '/pingzheng/api/pz/listPz',
                data: {
                        'kZtdm':ztdm,
                        'kKjnd':kjnd,
                        'kPzzt':'',
                        'kKjqjStart':kjqj,
                        'kKjqjEnd':kjqj,
                        'page':1,
                        'rows':1000
                        },
                success:function(result){
                    window.res=result;
                }});
            }'''
        # 创建数据库的infonameID
        infonameID = self.exportSql.init_infoname(infoname).id
        try:
            for Qj in Qjlist:
                kjnd = Qj[:4]
                kjqj = Qj[4:]
                voucherData = self.down.evaluate(js, ztdm=ztdm, kjnd=kjnd, kjqj=kjqj)

                # 保存到数据库
                voucherString = json.dumps(voucherData)
                self.exportSql.insert_new(zt_id, Qj, infonameID, voucherString)

        except Exception as e:
            msg = '凭证导出失败：{}'.format(str(e))
        else:
            msg = '凭证导出成功'

        return msg