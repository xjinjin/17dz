import time
import xlrd


class utils():
    def __init__(self):
        pass


# 获取excel中的公司名称
def get_company_name(file):
    xl = xlrd.open_workbook(file)
    sheet1 = xl.sheets()[0]
    com_list = sheet1.col_values(1)
    com_list.remove(com_list[0])
    return com_list


# todo:进入记账
def jizhang(browser, company):
    with browser.get_iframe('Conframe') as Conframe:
        search_func = Conframe.evaluate_script('doSearchMyCustomer.toString()')
        new_func = search_func.replace('success: function (data) {',
                                       'success: function (data) { window.Customerdata=data;')
        browser.evaluate_script('doSearchMyCustomer=%s' % new_func)

    with browser.get_iframe('Conframe') as Conframe:
        # 填写公司名称
        Conframe.find_by_css('input#CnameVal').first.fill(company)
        browser.evaluate_script('doSearchMyCustomer()')
        time.sleep(0.5)
        new_data = browser.evaluate_script('window.Customerdata')
        if new_data['total'] == 1:
            a = Conframe.find_by_text('记账').first
            exjs = a._element.get_attribute('onclick')
            Conframe.evaluate_script(exjs)
        else:
            return '没有找到数据'

    # 切换到第二页进行提取
    browser.windows.current = browser.windows[1]


# 获取当前公司名称
def company_name(browser):
    with browser.get_iframe('ifame_top') as the_iframe:
        company_name = the_iframe.find_by_css("div .searchable-select-holder")[0].text
    company = company_name.split('-')[1]

    return company


# 打开对应的tab
tab_list = {}


def open_tab(browser, tab_name):
    i = len(tab_list)
    if tab_name == 'voucher':
        # 打开查询凭证
        voucher = browser.find_by_css('ul.ac>li')[2]
        voucher.find_by_css('a[data-href="Voucher/voucher-list.html"]').first.click()
        tab_list['voucher'] = i
    elif tab_name == 'km':
        # 打开科目余额表
        zhangbu = browser.find_by_css('ul.ac>li')[3]
        zhangbu.find_by_css('a[href="javascript:void(0);"]').first.click()
        km = zhangbu.find_by_css('ul.ul_more>li')[2]
        km.find_by_css('a[data-href="Books/subject-balance.html"]').first.click()
        zhangbu.find_by_css('a[href="javascript:void(0);"]').first.click()
        tab_list['km'] = i
    elif tab_name == 'fzhs':
        # 打开辅助核算余额表
        zhangbu = browser.find_by_css('ul.ac>li')[3]
        zhangbu.find_by_css('a[href="javascript:void(0);"]').first.click()
        fzhs = zhangbu.find_by_css('ul.ul_more>li')[9]
        fzhs.find_by_css('a[data-href="Books/accounting-balance.html"]').first.click()
        zhangbu.find_by_css('a[href="javascript:void(0);"]').first.click()
        tab_list['fzhs'] = i
    elif tab_name == 'settings':
        # 打开基础设置
        settings = browser.find_by_css('ul.ac>li')[9]
        settings.find_by_css('a[href="javascript:void(0);"]').first.click()
        basicsettings = settings.find_by_css('ul.ul_more>li')[0]
        basicsettings.find_by_css('a[data-href="/Settings/BasicSettings/index.html"]').first.click()
        settings.find_by_css('a[href="javascript:void(0);"]').first.click()
        tab_list['base_set'] = i


if __name__ == '__main__':
    com_list = get_company_name('01方位杨娟账套.xlsx')
    print(com_list)
