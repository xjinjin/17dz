# -*- coding: utf-8 -*-
import base64
import time
from os import path
from flask import Flask, request, jsonify, session
from flask import redirect
from flask import render_template
from flask import url_for
from splinter.browser import Browser
# from . import open_tab, tab_list, company_name, jizhang
from public.JIZHI_dama import RClient
from public.utils import company_name, open_tab, tab_list, jizhang
from .mongo_data import *
import redis
from . import YDZ_blue


browser = Browser("chrome")


# 首页界面
# @app.route('/index')
# def index():
#     return render_template('index.html')


# 添加新账号
@YDZ_blue.route('/new_users', methods=['POST', 'GET'])
def new_users():
    # 获取新的用户信息
    data = request.form.to_dict()
    qyh = data.get('qyh')
    account = data.get('account')
    password = data.get('password')
    excel = data.get('excel')

    user_info = {
        'qyh': qyh,
        'account': account,
        'password': password,
        'excel': excel
    }

    # 添加到数据库
    try:
        new_user(user_info)
    except Exception as e:
        return jsonify(errorMsg=e)
    else:
        resp_data = {
            'errorMsg': ''
        }
        return jsonify(resp_data)


# 更新账号信息
@YDZ_blue.route('/update_user')
def update_user():
    pass


# 删除用户信息
@YDZ_blue.route('/deleted_users')
def deleted_users():
    return 'success'


@YDZ_blue.route('/admin')
def admin():

    browser.visit('http://www.yundaizhang.com/MobileRegister/mobileLogin.html')

    img_element = browser.find_by_css('img.register_pic')
    img_element.click()
    img = img_element.screenshot(full=True)
    with open(img, "rb") as f:
        img_data = base64.b64encode(f.read())

    img_msg = img_data.decode()

    # 将base64格式返回
    key = 'data:image/png;base64,%s' % img_msg

    # return jsonify(key='data:image/png;base64,%s' % img_msg)

    return render_template('login_form.html', img_code=key)


'''
@YDZ_blue.route('/index')
def index():
    # 登陆成功后跳转到首页
    # todo:通过上传的文件将对应的公司填到html中
    # 判断是否已经登陆

    return render_template('test.html')
'''


# 验证码截图
@YDZ_blue.route('/login1', methods=['GET', 'POST'])
def login1():
    # browser.visit('http://www.yundaizhang.com/MobileRegister/mobileLogin.html')

    # 企业号码，账号，密码，
    login_data = request.json

    qyh = login_data.get('qyh')
    acccount = login_data.get('account')
    password = login_data.get('password')
    # excel_file = login_data.files('file')
    # file = request.files['file']

    # 校验是否为空
    if not all([qyh, acccount, password]):
        return jsonify(errmsg='参数不全')

    img_element = browser.find_by_css('img.register_pic')
    img_element.click()
    img = img_element.screenshot(full=True)

    # 调用打码平台 得到结果
    rc = RClient('cicjust', 'JYcxys@3030')

    im = open(img, 'rb').read()

    result_msg = rc.rk_create(im, 3000)

    resp_code = result_msg['code']
    # resp_code = 20000

    if resp_code == 10000:
        img_code = result_msg['data']['result']
        # 识别成功，直接填写登陆

        # 获取企业号输入标签
        browser.find_by_id('txt_qyh').fill(qyh)

        # 获取账号输入标签
        browser.find_by_id('txt_uid').fill(acccount)

        # 获取密码输入标签
        browser.find_by_id('txt_pwd').fill(password)

        # 获取验证码输入标签
        browser.find_by_id('txt_yzm').fill(img_code)

        # 登陆按钮
        login_button = browser.find_by_xpath("//li[@class='login_list login_submit_btn login_submit_btn1']")

        # 点击登陆后判断是否成功
        login_button.click()
        time.sleep(2)

        try:
            # 登陆失败后返回的提示信息
            result = browser.get_alert()
        except:

            if browser.title == 'CRS':
                time.sleep(1)
                jizhang(browser, '安徽汇乐智能科技有限公司')
                return jsonify(msg='success')
        else:
            result_msg = result.text
            if result_msg:
                # 点击确定
                result.accept()
                return jsonify(msg=result_msg)

    # 识别失败，返回验证码截图
    else:
        return jsonify(msg='请刷新后登陆')



# 当第一次返回的是截图信息的时候，访问此登陆接口
# 参数 [login_data，qyh，count，password，img_code]
@YDZ_blue.route('/login2', methods=['POST'])
def login2():
    # 企业号码，账号，密码，验证码
    login_data = request.json
    qyh = login_data.get('qyh')
    account = login_data.get('account')
    password = login_data.get('password')
    img_code = login_data.get('img_code')

    # 校验是否为空
    if not all([qyh, account, password, img_code]):
        return jsonify(errmsg='参数不全')

    # 获取企业号输入标签
    browser.find_by_id('txt_qyh').fill(qyh)

    # 获取账号输入标签
    browser.find_by_id('txt_uid').fill(account)

    # 获取密码输入标签
    browser.find_by_id('txt_pwd').fill(password)

    # 获取验证码输入标签
    browser.find_by_id('txt_yzm').fill(img_code)

    # 登陆按钮
    login_button = browser.find_by_xpath("//li[@class='login_list login_submit_btn login_submit_btn1']")

    # 点击登陆后判断是否成功
    login_button.click()

    time.sleep(1.5)

    try:
        # 登陆失败后返回的提示信息
        result = browser.get_alert()
    except:

        if browser.title == 'CRS':
            # todo:进入记账页面
            time.sleep(1)
            # 进入记账页面
            jizhang(browser, '安徽汇乐智能科技有限公司')
            return jsonify(msg='success')
    else:
        result_msg = result.text
        if result_msg:
            # 点击确定
            result.accept()
            return jsonify(msg=result_msg)

            # 将对象保存到session中
            # next_page = browser.windows.current._browser
            # session['next_page'] = next_page


# 凭证
@YDZ_blue.route('/voucher', methods=['GET'])
def voucher():
    # 点击记账
    # with browser.get_iframe('Conframe') as first_iframe:
    #     browser.evaluate_script("enter('432b8eb2-cdab-4b5c-82b8-127995617544','曹诚','da4c0828-a4fc-491a-8a6e-728374902bc8')")

    time.sleep(3)
    # 切换到第二页进行提取
    browser.windows.current = browser.windows[1]

    # 打开查询凭证
    open_tab(browser, 'voucher')
    iframe_index = tab_list['voucher'] + 3

    # 点击查询按钮
    with browser.get_iframe(iframe_index) as last_iframe:
        div = last_iframe.find_by_css('.search')
        div.find_by_css('input.button_search')[0].click()

        # 得到总期数,修改pagesize
        total_count = browser.evaluate_script("vchStartPeriodCombo.getCombo().rawData.length")
        load_data = browser.evaluate_script("loadData.toString()")
        # 替换pagesize
        page_data = load_data.replace("var pagesize = $('#pagesize').val();", "var pagesize = 500")
        browser.evaluate_script('loadData=%s' % page_data)
        # 得到响应的data
        voucher_data = page_data.replace("if (data.status == 200) {",
                                         "window.voucherdata = data; if (data.status == 200) {")
        browser.evaluate_script('loadData=%s' % voucher_data)

        # 添加获取当前期数
        date_time = voucher_data.replace("var endperiod = parseInt(vcheEndPeriodCombo.getCombo().getValue());",
                                         "var endperiod = parseInt(vcheEndPeriodCombo.getCombo().getValue()); "
                                         "window.startdate = startperiod; "
                                         "window.enddate = endperiod;")
        browser.evaluate_script('loadData=%s' % date_time)

        voucher_dict = {}

        # 循环导出
        for i in range(total_count):
            # 填充 起始
            browser.evaluate_script("vchStartPeriodCombo.getCombo().selectByIndex(%s)" % i)
            # 填充 结尾
            browser.evaluate_script("vcheEndPeriodCombo.getCombo().selectByIndex(%s)" % i)

            # 点击 查询
            div.find_by_css('input.button_search')[0].click()
            time.sleep(2)

            # 得到对应的期数
            startdate = browser.evaluate_script("window.startdate")
            # enddate = browser.evaluate_script("window.enddate")

            # 得到查询的数据
            data = browser.evaluate_script("window.voucherdata")

            if not data:
                voucher_dict[str(startdate)] = '暂无数据'

            # 加入凭证
            voucher_dict[str(startdate)] = data

            # 捕获弹窗alert
            try:
                alert_msg = browser.get_alert()
            except:
                continue
            else:
                alert_msg.accept()

    # 得到当前页面的公司名称
    company = company_name(browser)

    # 进行凭证的保存
    try:
        update_voucher(company, voucher_dict)
    except:
        raise
    finally:
        return redirect(url_for(kmsheet))


# 科目余额表
@YDZ_blue.route('/kmsheet', methods=['GET'])
def kmsheet():
    # 打开科目余额表
    open_tab(browser, 'km')
    iframe_index = tab_list['km']

    with browser.get_iframe(iframe_index) as last_iframe:
        browser.find_by_css('input#startPeriodY').first.click()

    # 得到年份列表
    year_list = []
    with browser.get_iframe(iframe_index + 1) as last_iframe:
        year_li = browser.find_by_css('td[nowrap="nowrap"]')
        for year in year_li:
            year_list.append(year.text.split()[0])

    # 得到当前月份列表
    month_list = []
    with browser.get_iframe(iframe_index) as last_iframe:
        browser.find_by_css('input#startPeriodM').first.click()
        month_li = browser.find_by_css('ul#startM>li[data-value]')
        for month in month_li:
            month_list.append(month.text)

    with browser.get_iframe(iframe_index) as last_iframe:
        # 勾选本年累计发生额和辅助核算
        init_func = browser.evaluate_script('initEvent.toString()')
        init_isshow = init_func.replace('$("#isshow").change(function () {',
                                        '$("#isshow").change(function () { $(this).attr("checked") = "checked";')
        init_isfzhs = init_isshow.replace('$("#isfzhs").change(function () {',
                                          '$("#isfzhs").change(function () { $(this).attr("checked") = "checked";')
        browser.evaluate_script('initEvent=%s' % init_isfzhs)

        # 更改科目级别和科目类目和小计以及金额显示
        load_func = browser.evaluate_script('loadData.toString()')
        fLevel = load_func.replace("var fLevel = $('#fLevel').attr('data-value');", "var fLevel = 5")
        ischeck = fLevel.replace('''var ischeck = $("#ischeck").attr("checked") == 'checked' ? "1" : "0";''',
                                 'var ischeck = 1')
        category = ischeck.replace('''var category = groupCombo.getCombo().getValue();''', 'var category = 0')
        isxiaoji = category.replace('''var isxiaoji = $("#isxiaoji").attr("checked") == 'checked' ? "1" : "0";''',
                                    'var isxiaoji = 1')
        kmdata = isxiaoji.replace('success: function (data) {', 'success: function (data) { window.kmdata=data;')

        # 当第一个年份为2018年时，设置为2018年，并循环遍历后面的月份，其他的年份不管
        KMSheet = {}
        # year_list[0] = '2017'
        if year_list[0] == '2018':
            KMSheet['2018'] = {}
            fyear = kmdata.replace("fYear = $('#startPeriodY').val();", "fYear = '2018'")

            # todo:得到这一年的对应的月份

            for m in month_list:
                # 替换月份
                startFPeriod = fyear.replace("startFPeriod = $('#startPeriodM').val();", "startFPeriod = %s" % m)
                endFPeriod = startFPeriod.replace("endFPeriod = $('#endPeriodM').val();", "endFPeriod = %s" % m)
                browser.evaluate_script('loadData=%s' % endFPeriod)
                # 点击查询
                last_iframe.find_by_css('input[value="查询"]').first.click()
                # 获得结果
                result_msg = browser.evaluate_script("window.kmdata")

                if not result_msg:
                    KMSheet['2018'][m] = '暂无数据'

                # 放进字典
                KMSheet['2018'][m] = result_msg

    # 得到当前页面的公司名称
    company = company_name(browser)
    try:
        update_kmsheet(company, KMSheet)
    except:
        raise Exception
    finally:
        return redirect(url_for(fzSheet))


# 辅助核算余额表
@YDZ_blue.route('/fzSheet', methods=['GET'])
def fzSheet():
    # 打开辅助核算余额表
    open_tab(browser, 'fzhs')
    iframe_index = tab_list['fzhs'] + 3

    # 点开年份按钮
    with browser.get_iframe(iframe_index) as last_iframe:
        browser.find_by_css('input#startPeriodY').first.click()

    # 得到年份列表
    year_list = []
    with browser.get_iframe(iframe_index + 1) as last_iframe:
        year_li = browser.find_by_css('td[nowrap="nowrap"]')
        for year in year_li:
            year_list.append(year.text.split()[0])

    # 得到当前月份列表
    month_list = []
    with browser.get_iframe(iframe_index) as last_iframe:
        browser.find_by_css('input#startPeriodM').first.click()
        month_li = browser.find_by_css('ul#startM>li[data-value]')
        for month in month_li:
            month_list.append(month.text)

    with browser.get_iframe(iframe_index) as last_iframe:
        load_func = browser.evaluate_script('loadData.toString()')
        # 勾选金额为0不显示按钮
        ischeck = load_func.replace("""ischeck = $("#ischeck").attr("checked") == 'checked' ? "1" : "0";""",
                                    "ischeck = 1")

        # 替换响应的data
        fzdata = ischeck.replace('success: function (data) {', 'success: function (data) { window.fzdata=data;')

        # 当第一个年份为2018年时，设置为2018年，并循环遍历后面的月份，其他的年份不管
        FZSheet = {}
        # year_list[0] = '2017'
        if year_list[0] == '2018':
            FZSheet['2018'] = {}
            fyear = fzdata.replace("fYear = $('#startPeriodY').val();", "fYear = '2018'")

            for m in month_list:
                # 替换月份
                startFPeriod = fyear.replace("startFPeriod = $('#startPeriodM').val();", "startFPeriod = %s" % m)
                endFPeriod = startFPeriod.replace("endFPeriod = $('#endPeriodM').val();", "endFPeriod = %s" % m)
                browser.evaluate_script('loadData=%s' % endFPeriod)
                # 点击查询
                last_iframe.find_by_css('input[value="查询"]').first.click()
                # 获得结果
                result_msg = browser.evaluate_script("window.fzdata")

                if not result_msg:
                    kmsheet['2018'][m] = '暂无数据'

                # 放进字典
                FZSheet['2018'][m] = result_msg

    # 得到当前页面的公司名称
    company = company_name(browser)
    try:
        update_fzsheet(company, FZSheet)

    except:
        return jsonify('辅助核算余额表导出失败')
    finally:
        return redirect(url_for(settings))


@YDZ_blue.route('/settings', methods=['GET'])
def settings():
    # 打开基础设置
    open_tab(browser, 'settings')
    iframe_index = tab_list['base_set'] + 3

    # base_setting = browser.find_by_css('ul.ac>li')[9]
    # base_setting.find_by_css('a[href="javascript:void(0);"]').first.click()
    # li = base_setting.find_by_css('ul.ul_more>li')[0]
    # li.find_by_css('a[data-href="/Settings/BasicSettings/index.html"]').first.click()

    # 点击科目按钮
    with browser.get_iframe(iframe_index) as new_iframe:
        new_iframe.find_by_css('li[title="科目"]').first.click()

    km_dict = {}
    with browser.get_iframe(iframe_index) as new_iframe:
        with browser.get_iframe('frametitle') as frametitle:
            func = browser.evaluate_script('loadSubjectByCategory.toString()')
            data = func.replace('success: function (data) {', 'success: function (data) { window.respdata=data;')
            browser.evaluate_script('loadSubjectByCategory=%s' % data)
            # 得到所有的data-id
            element_list = frametitle.find_by_css('a[data-id]')
            for element in element_list:
                id = element._element.get_attribute('data-id')
                name = element.value
                # 点击资产按钮
                frametitle.find_by_css('a[data-id="%s"]' % id).first.click()
                data = browser.evaluate_script('window.respdata')
                km_dict[name] = data

    # 得到当前页面的公司名称
    company = company_name(browser)

    try:
        # 将基础设置的科目更新到数据库
        update_setting_km(company, km_dict)
    except:
        return jsonify(msg='科目设置导出失败')

    # 点击币别
    bibie = []
    with browser.get_iframe(iframe_index) as new_iframe:
        new_iframe.find_by_css('li[title="币别"]').first.click()
        with browser.get_iframe('frametitle') as frametitle:
            m_list = frametitle.find_by_css('table[class="content"]').find_by_css('td')
            m_list.pop()
            for i in m_list:
                bibie.append(i.text)

    try:
        # 将基础设置的科目更新到数据库
        update_setting_bibie(company, bibie)
    except:
        return jsonify(msg='币别设置导出失败')

    # 点击辅助核算
    fzhs_dict = {}
    with browser.get_iframe(iframe_index) as new_iframe:
        # 点击辅助核算
        new_iframe.find_by_css('li[title="辅助核算"]').first.click()
        # 点击客户
        with browser.get_iframe('frametitle') as frametitle:
            frametitle.find_by_css('a[class="bg1"]').first.click()
    with browser.get_iframe(iframe_index + 1) as iframe:
        gid_list = iframe.find_by_css('ul[id="top_tab"]>li>a[name="gd"]')
        js = '''get_gid=function (gid) {
                        $.ajax({
                            type: "POST",
                            url: "../../Ajax/assisting.ashx",
                            data: { key: 'getassisting', acid: gid, ztID: SYSTEM.SessionKey },
                            dataType: "json",
                            async: false,
                            success: function (data) {
                                top.loaddata=data
                                }
                        }'''
        browser.evaluate_script(js)

        for i in gid_list:
            name = i.text
            gid = i._element.get_attribute('data-gid')

            browser.evaluate_script('get_gid("%s")' % gid)

            data = browser.evaluate_script('top.loaddata')

            if not data:
                fzhs_dict[name] = '暂无数据'

            fzhs_dict[name] = data
    try:
        # 将基础设置的辅助核算更新到数据库
        update_setting_fzhs(company, fzhs_dict)
    except:
        return jsonify(msg='导出失败')

    return jsonify(msg='辅助核算设置导出成功')


