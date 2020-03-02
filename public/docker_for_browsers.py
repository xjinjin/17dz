# -*- coding:utf-8 -*-
from splinter.driver.webdriver.remote import WebDriver as RemoteWebDriver

# RemoteWebDriver(url='http://127.0.0.1:4444/wd/hub',browser='chrome')


class DockerForBrowsers():

    def __init__(self,conn_url):

        self.url = conn_url
        self.browser = 'chrome'

    def connect_to_browser(self):

        browser = RemoteWebDriver(url=self.url,browser=self.browser)

        return browser