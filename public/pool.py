
from selenium import webdriver
from splinter import Browser
import time


class PoolOptions(object):
    """
    定义BrowserPool的属性
    """
    # 定义该对象能绑定的属性值
    __slots__ = ('__max_pool_size', '__min_pool_size', '__wait_times', '__load_timeouts')

    def __init__(self, max_pool_size=8, min_pool_size=2, wait_times=300, load_timeouts=100):
        self.__max_pool_size = max_pool_size
        self.__min_pool_size = min_pool_size
        self.__wait_times = wait_times
        self.__load_timeouts = load_timeouts

    @property
    def max_pool_size(self):
        return self.__max_pool_size

    @property
    def min_pool_size(self):
        return self.__min_pool_size

    @property
    def wait_times(self):
        return self.__wait_times

    @property
    def load_timeouts(self):
        return self.__load_timeouts

    @max_pool_size.setter
    def max_pool_size(self, num):
        self.__max_pool_size = num

    @min_pool_size.setter
    def min_pool_size(self, num):
        self.__min_pool_size = num

    @wait_times.setter
    def wait_times(self, num):
        self.__wait_times = num

    @load_timeouts.setter
    def load_timeouts(self, num):
        self.__load_timeouts = num


class Pool(object):
    """
    BrowserPool
    """
    NOT_BRO_LIST = []  # 已被使用的browser
    BRO_LIST = []  # 可用browser

    def __init__(self, options):
        """
        Pool的构造函数
        :param options: 一个PoolOptions对象
        """
        self.opt = options
        self.__cross_domain = webdriver.ChromeOptions().add_argument('--disable-web-security --user-data-dir')
        self.__check_num()

    def __create_browser(self, bro_type):
        """
        创建一个新的浏览器对象
        :param bro_type: 浏览器类型
        :return: 一个浏览器对象
        """
        browser = Browser(bro_type, self.__cross_domain,headless=True)
        browser.bro_type = bro_type
        browser.bro_time = time.time()
        browser.bro_statu = False
        browser.driver.set_page_load_timeout(self.opt.load_timeouts)
        browser.driver.set_script_timeout(self.opt.load_timeouts)
        self.BRO_LIST.append(browser)
        return browser

    def clean_pool(self):
        """
        将可用的pool中失效的browser清除
        :return:布尔值
        """
        for i in range(len(self.BRO_LIST)):
            try:
                self.BRO_LIST[i].reload()
            except Exception as e:
                print('clean_pool方法捕获异常！该损坏浏览器已经删除！')
                print('异常信息：', e)
                self.BRO_LIST.pop(i)

    def __check_num(self):
        """
        检查browserpool的BRO_LIST中的browser数量是否合法
        :return: 无
        """
        for i in range(self.opt.min_pool_size):
            if len(self.BRO_LIST) < self.opt.min_pool_size and \
                    len(self.BRO_LIST) + len(self.NOT_BRO_LIST) < self.opt.max_pool_size:
                self.__create_browser('chrome')

    def __listen_browser(self):
        """
        监听pool中browser的数量是否合法
        :return: 布尔值
        """
        if len(self.BRO_LIST)+len(self.NOT_BRO_LIST) < self.opt.max_pool_size:
            flag = True
        else:
            if len(self.BRO_LIST) > 0:
                browser = self.BRO_LIST.pop()
                browser.quit()
                del browser
                flag = True
            else:
                flag = False
        return flag

    def get_browser(self, bro_type, bro_user):
        """
        从可用浏览器列表中筛选出合适的浏览器对象并将该对象返回，若没有合适的对象则创建一个对象返回
        :param bro_type: 浏览器类型
        :param bro_user: 浏览器使用者
        :return: 当内存足够时返回一个browser对象，内存资源不足时返回布尔值False
        """
        for i in range(len(self.BRO_LIST)):
            try:
                if not self.BRO_LIST[i].bro_statu and self.BRO_LIST[i].bro_type == bro_type:
                    self.BRO_LIST[i].reload()
                    self.BRO_LIST[i].bro_statu = True
                    self.BRO_LIST[i].bro_user = bro_user
                    self.BRO_LIST[i].bro_time = time.time()
                    self.NOT_BRO_LIST.append(self.BRO_LIST[i])
                    browser = self.BRO_LIST.pop(i)
                    return browser
                else:
                    pass
            except Exception as e:
                # print(e)
                self.BRO_LIST.pop(i)
                continue
        if self.__listen_browser():
            browser = self.__create_browser(bro_type)
            browser.bro_statu = True
            browser.bro_user = bro_user
            browser.bro_time = time.time()
            self.BRO_LIST.pop()
            self.NOT_BRO_LIST.append(browser)
            return browser
        else:
            print('内存资源不足！')
            return False

    def close_browser(self, browser):
        """
        当一个浏览器不需要时将其从不可用列表移动至可用列表，若该浏览器已经崩溃，则直接删除
        :param browser: 需要断开链接的浏览器
        :return: 布尔值
        """
        try:
            for i in range(len(self.NOT_BRO_LIST)):
                if id(self.NOT_BRO_LIST[i]) == id(browser):
                    try:
                        browser.reload()
                    except Exception as e1:
                        print(e1)
                        browser = self.NOT_BRO_LIST.pop(i)
                        del browser
                        return True
                    browser.bro_statu = False
                    browser.bro_time = time.time()
                    self.BRO_LIST.append(browser)
                    self.NOT_BRO_LIST.pop(i)
                    return True
                else:
                    pass
        except Exception as e:
            # print('未知异常，浏览器断开链接（close_browser）执行失败')
            print('异常信息：', e)
            return False
