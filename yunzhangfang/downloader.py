# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

class Chrome():
    def __init__(self,browser,**kwargs):
        '''配置Chrome'''
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')

        # self.browser = Browser("chrome", options=chrome_options)
        self.browser = browser

        if 'page_timeout' in kwargs:
            page_timeout = int(kwargs['page_timeout'])
            self.browser.driver.set_page_load_timeout(page_timeout)
        if 'script_timeout' in kwargs:
            script_timeout = int(kwargs['script_timeout'])
            self.browser.driver.set_script_timeout(script_timeout)


    def down(self, url):
        '''请求网页'''
        self.browser.visit(url)


    def evaluate(self, js='', username='', password='', kjnd='', kjqj='', qyid='', ztdm='',bzid=''):
        '''执行代码'''
        self.browser.evaluate_script('window.res=""')
        i = 0
        while True:
            if i > 5:
                return 'js错误'
            try:
                self.browser.evaluate_script(js)
                break
            except Exception as e:
                i += 1
                continue
        try:
            self.browser.evaluate_script(
                'script("%s","%s","%s","%s","%s","%s","%s")' % (username, password, kjnd, kjqj, qyid, ztdm,bzid))
            res = self.browser.evaluate_script('window.res')
            if not res:
                raise TimeoutException
        except TimeoutException as e:
            while True:
                res = self.browser.evaluate_script('window.res')
                if res:
                    return res
        else:
            return res
