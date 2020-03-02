# -*- coding: utf-8 -*-
import json
import os
import tempfile
import time
import datetime
from PIL import Image
# from six import BytesIO
from io import BytesIO
from public.JIZHI_dama import RClient


class GetInfo():
    conn = ''
    browser = ''

    def __init__(self, browser, conn=None, to_sql=None):

        # 数据库存储初始化 表名称、登陆用户名
        self.exportSql = to_sql
        self.browser = browser
        self.conn = conn

    # 验证码截图,登陆
    def login(self, info):
        self.browser.driver.set_window_size(1600, 1000)
        self.browser.visit('https://sap.kungeek.com/portal/login.jsp?top')

        if self.browser.url == 'https://sap.kungeek.com/portal/ftsp/portal/home.do?main':
            return '登陆成功'

        # 账号，密码，
        account = info.get('account')
        password = info.get('password')

        # 校验是否为空
        if not all([account, password]):
            return '参数不全'

        # 进行窗口截图，计算大小
        full_screen_png = self.browser.driver.get_screenshot_as_png()
        full_screen_bytes = BytesIO(full_screen_png)
        im = Image.open(full_screen_bytes)
        im_width, im_height = im.size[0], im.size[1]
        window_size = self.browser.driver.get_window_size()
        window_width = window_size['width']

        ratio = im_width * 1.0 / window_width
        height_ratio = im_height / ratio

        im = im.resize((int(window_width), int(height_ratio)))
        img_element = self.browser.find_by_css('img#logCode_img')
        location = img_element._element.location
        # 验证码的位置
        x, y = location['x'], location['y']

        # 验证码的宽高
        pic_size = img_element._element.size
        w, h = pic_size['width'], pic_size['height']

        # 调整偏移量
        box = x + 1, y + 3, x + w + 2, y + h
        box = [int(i) for i in box]
        target = im.crop(box)
        (fd, filename) = tempfile.mkstemp(prefix='', suffix='.png')
        os.close(fd)
        target.save(filename)
        im = open(filename, 'rb').read()

        # 调用打码平台 得到结果
        rc = RClient('cicjust', 'JYcxys@3030')

        result_msg = rc.rk_create(im, 3000)

        resp_code = result_msg['code']

        if resp_code == 10000:
            img_code = result_msg['data']['result']
            # 识别成功，直接填写登陆

            # 获取账号输入标签
            self.browser.find_by_id('j_username').fill(account)

            # 获取密码输入标签
            self.browser.find_by_id('j_password').fill(password)

            # 获取验证码输入标签
            self.browser.find_by_id('logCode').fill(img_code)

            # 登陆按钮
            login_button = self.browser.find_by_id('btn-login')

            # 点击登陆后判断是否成功
            login_button.click()
            time.sleep(1)

            url = self.browser.url
            if 'login_error' in url:
                error_msg = url.split('=')[1]

                if error_msg == 'user_not_found':
                    return '账号和密码不匹配,请重新输入'
                elif error_msg == 'verify_code_error':
                    return '验证码错误,请重新输入'
                elif error_msg == 'user_disabled':
                    return '账号已停用或合同未审核通过'
                elif error_msg == 'user_locked':
                    return '账号不存在或已停用'

            elif url == 'https://sap.kungeek.com/portal/ftsp/portal/home.do?main':

                return '登陆成功'

        # 识别失败
        else:
            return '打码平台故障'

    # 登陆成功后获取账套列表
    def getAllzt(self):

        # self.browser.find_by_text('凭证查看').first.click()

        js = ''' getAllzt=function () {
            var params = {} ;
            params.url = 'https://sap.kungeek.com/portal/ftsp/portal/form.do?getAllCustomers' ;
            params.data = {pageIndex: 1, pageSize: 10000};
            params.callback = function(result){
                if(result.success) {
                    top.zt_data = result.data;
                } else {
                    top.zt_data = result.errMsg;
                }

            };
            ftsps.ajax.postData(params) ;
        }'''

        self.browser.evaluate_script(js)

        self.browser.evaluate_script('getAllzt()')
        i = 1
        while True:
            if self.browser.evaluate_script("top.zt_data"):
                ztData = self.browser.evaluate_script('top.zt_data')
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
    def switchZt(self, ztId, khId):

        js = '''getKhxx = function (ztZtxxId, khxxId) {
                var params = new Object() ;
                params.url = 'https://sap.kungeek.com/portal/ftsp/portal/khxx.do?handleCustomer' ;
                params.showLoading = 'N' ;
                params.async = false ;
                params.data = {ztZtxxId: ztZtxxId, khxxId: khxxId} ;
                params.callback = function(result) {
                    if(result.success) {
                        top.khxx = result.data;
                    } else {
                        top.khxx = result.errMsg;
                    }
                };
                ftsps.ajax.postData(params) ;
            }'''

        self.browser.evaluate_script(js)

        self.browser.evaluate_script('getKhxx("%s","%s")' % (ztId, khId))
        i = 1
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

        startQj = khxx['qyQj']
        endQj = khxx['currYear'] + khxx['currMonth']

        dateStart = datetime.datetime.strptime(startQj, '%Y%m')
        dateEnd = datetime.datetime.strptime(endQj, '%Y%m')

        dates = []
        while dateStart < dateEnd:
            dateStart += datetime.timedelta(weeks=4)
            dates.append(dateStart.strftime('%Y%m'))

        datesList = sorted(list(set(dates)))

        return datesList

    # 凭证
    def voucher(self, QjList, ztId, zt_id, infoname):

        js = '''get_Voucher=function(ztId,kjqj_date){
                $.ajax({
                    type: "POST",
                    url: 'https://sap.kungeek.com/portal/ftsp/portal/voucher.do?selectVoucherList',
                    data: { ztZtxxId:ztId, kjQj:kjqj_date, pageIndex:1, pageSize:99999 },
                    dataType: "json",
                    success: function (result) {
                        if(result.success) {
                            top.voucher_data = result.data;
                        } else {
                            top.voucher_data = result.errMsg;
                        }
                    }
                })
            }
            '''

        self.browser.evaluate_script(js)
        # 创建数据库的infonameID
        infonameID = self.exportSql.init_infoname(infoname).id
        try:

            for Qj in QjList:
                voucher_data = {}
                self.browser.evaluate_script('get_Voucher("%s","%s")' % (ztId, Qj))
                i = 1
                while True:
                    if self.browser.evaluate_script("top.voucher_data"):
                        data = self.browser.evaluate_script('top.voucher_data')
                        voucher_data = data.get('data')
                        break
                    elif i > 5:
                        break
                    else:
                        time.sleep(0.5)
                        i += 1
                        pass
                self.browser.evaluate_script('top.voucher_data=""')

                # 保存到数据库
                voucherString = json.dumps(voucher_data)
                self.exportSql.insert_new(zt_id, Qj, infonameID, voucherString)

        except Exception as e:
            msg = '凭证导出失败：{}'.format(str(e))

        else:
            msg = '凭证导出成功'

        return msg

    # 科目余额表
    def kmsheet(self, QjList, ztId, zt_id, infoname):

        js = '''getKmsheet=function (ztId,kjqj){

            var params = {};

            params.url = 'https://sap.kungeek.com/portal/ftsp/portal/balance.do?selectYebKmye';

            params.data = {
                    ztZtxxId: ztId,
                    ztCurrencyId: "",
                    xmId : "",
                    startKjQj: kjqj,
                    endKjQj: kjqj,
                    isRMB:"",
            } ;
            params.callback = function(result){
                if(result.success) {
                    top.km_data = result.data;
                } else {
                    top.km_data = result.errMsg;
                }

            } ;
            ftsps.ajax.postData(params) ;
        }'''

        self.browser.evaluate_script(js)

        js_wl = '''getWlmx=function (ztId,kjqj){

            var params = {} ;

            params.url = 'https://sap.kungeek.com/portal/ftsp/portal/balance.do?getYebWangLaiMx&funcCode=ftsp_zhangbu_balance';

            params.data = {
                    ztZtxxId: ztId,
                    currencyId: "",
                    xmId: "",
                    startKjQj: kjqj,
                    endKjQj: kjqj,
            } ;
            params.callback = function(result){
                if(result.success) {
                    top.wl_data = result.data;
                } else {
                    top.wl_data = result.errMsg;
                }

            } ;
            ftsps.ajax.postData(params) ;
        }'''

        self.browser.evaluate_script(js_wl)

        # 创建数据库的infonameID
        infonameID = self.exportSql.init_infoname(infoname).id
        try:
            for Qj in QjList:

                self.browser.evaluate_script('getKmsheet("%s","%s")' % (ztId, Qj))
                self.browser.evaluate_script('getWlmx("%s","%s")' % (ztId, Qj))

                i = 1
                km_data = {}
                while True:
                    if self.browser.evaluate_script("top.km_data"):
                        data_km = self.browser.evaluate_script('top.km_data')
                        data_wl = self.browser.evaluate_script('top.wl_data')

                        km_data = {}
                        km_data['KM'] = data_km
                        km_data['wlmx'] = data_wl
                        break
                    elif i > 5:
                        break
                    else:
                        time.sleep(0.5)
                        i += 1
                        pass
                self.browser.evaluate_script('top.km_data=""')
                self.browser.evaluate_script('top.wl_data=""')

                # 保存到数据库
                kmString = json.dumps(km_data)
                self.exportSql.insert_new(zt_id, Qj, infonameID, kmString)

        except Exception as e:
            msg = '科目余额表保存失败:%s' % e
        else:
            msg = '科目余额表导出成功'
        return msg

    # 会计科目
    def kjkmsheet(self, ztId, zt_id, infoname):
        Qj = ''
        js = '''get_KjkmList=function (ztId) {
            var params = {};
            params.url = 'https://sap.kungeek.com/portal/ftsp/portal/kjkm.do?queryAll';
            params.data = {ztZtxxId: ztId};
            params.callback = function(result){
                if(result.success) {
                    top.kjkm_data = result.data;
                } else {
                    top.kjkm_data = result.errMsg;
                }
            };
            ftsps.ajax.postData(params) ;
        }'''

        self.browser.evaluate_script(js)
        # 创建数据库的infonameID
        infonameID = self.exportSql.init_infoname(infoname).id
        try:
            self.browser.evaluate_script('get_KjkmList("%s")' % ztId)
            i = 1
            kjkm_data = {}
            while True:
                if self.browser.evaluate_script("top.kjkm_data"):
                    kjkm_data = self.browser.evaluate_script('top.kjkm_data')
                    break
                elif i > 5:
                    break
                else:
                    time.sleep(0.5)
                    pass

            self.browser.evaluate_script('top.kjkm_data=""')

            # 保存到数据库
            kjkmString = json.dumps(kjkm_data)
            self.exportSql.insert_new(zt_id, Qj, infonameID, kjkmString)

        except Exception as e:
            return '会计科目保存失败:%s' % e

        return '会计科目导出成功'

    # 基础设置
    def settings(self, ztId, zt_id,infoname):
        Qj = ''
        try:
            self.browser.find_by_text('基础设置').first.click()
            # 往来单位
            dw_url = 'https://sap.kungeek.com/portal/ftsp/portal/ztsz/wldw.do?queryAll'
            dw_data = self.get_settings(dw_url, ztId)['data']
            time.sleep(0.5)
            # 创建数据库的infonameID
            infonameID = self.exportSql.init_infoname(infoname+'-往来单位').id
            # 保存到数据库
            dwString = json.dumps(dw_data)
            self.exportSql.insert_new(zt_id, Qj, infonameID, dwString)

            # 存货
            ch_url = 'https://sap.kungeek.com/portal/ftsp/portal/ztsz/chxx.do?queryAll'
            ch_data = self.get_settings(ch_url, ztId)['data']['data']
            time.sleep(0.5)
            # 创建数据库的infonameID
            infonameID = self.exportSql.init_infoname(infoname+'-存货').id
            # 保存到数据库
            kmString = json.dumps(ch_data)
            self.exportSql.insert_new(zt_id, Qj, infonameID, kmString)

            # 项目
            xm_url = 'https://sap.kungeek.com/portal/ftsp/portal/ztsz/xmsz.do?query'
            xm_data = self.get_settings(xm_url, ztId)['data']
            time.sleep(0.5)
            # 创建数据库的infonameID
            infonameID = self.exportSql.init_infoname(infoname+'-项目').id
            # 保存到数据库
            xmString = json.dumps(xm_data)
            self.exportSql.insert_new(zt_id, Qj, infonameID, xmString)

            # 币别
            bibie_url = 'https://sap.kungeek.com/portal/ftsp/portal/ztsz/bbhl.do?queryBblb'
            bibie_data = self.get_settings(bibie_url, ztId)['data']
            if bibie_data == 'null':
                bibie_data = ''
            time.sleep(0.5)
            # 创建数据库的infonameID
            infonameID = self.exportSql.init_infoname(infoname+'-币别').id
            # 保存到数据库
            bibieString = json.dumps(bibie_data)
            self.exportSql.insert_new(zt_id, Qj, infonameID, bibieString)

        except Exception as e:
            msg = '基础设置导出失败:{}'.format(str(e))
        else:
            msg = '基础设置导出成功'
        return msg


    def get_settings(self, url, ztId):

        js = '''get_settings=function (url,ztId){
            var ajaxParam = {
                    ztZtxxId : ztId,
                    keyword: '',
                    ztCplxId: '',
                    ztSrlxId: ''
                };
            ajaxParam.pageIndex = 1;
            ajaxParam.pageSize = 99999;

            var params = {};
            params.url = url ;
            params.data = ajaxParam;
            params.callback = function(result){
                if(result.success) {
                    top.load_data = result;
                }else {
                    top.load_data = result;
                }
            } ;
            ftsps.ajax.postData(params) ;
        }'''

        try:
            self.browser.evaluate_script(js)

            self.browser.evaluate_script('get_settings("%s","%s")' % (url, ztId))
        except Exception as e:
            print(e)
        i = 1
        data = {}
        while True:
            if self.browser.evaluate_script("top.load_data"):
                data = self.browser.evaluate_script('top.load_data')
                break
            elif i > 5:
                break
            else:
                time.sleep(0.5)
                i += 1
                pass

        self.browser.evaluate_script('top.load_data=""')

        return data
