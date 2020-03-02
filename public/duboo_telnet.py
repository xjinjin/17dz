#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socket
import telnetlib

class dubbo:
    # 定义私有属性
    __init = False
    __encoding = "gbk"
    __finish = b'dubbo>'
    __connect_timeout = 10
    __read_timeout = 10

    # 定义构造方法
    def __init__(self, host, port):
        self.host = host
        self.port = port
        if host is not None and port is not None:
            self.__init = True

    def set_finish(self, finish):
        '''
        defualt is ``dubbo>``
        '''
        self.__finish = finish

    def set_encoding(self, encoding):
        '''
        If ``result retured by dubbo`` is a ``str`` instance and is encoded with an ASCII based encoding
        other than utf-8 (e.g. latin-1) then an appropriate ``encoding`` name
        must be specified. Encodings that are not ASCII based (such as UCS-2)
        are not allowed and should be decoded to ``unicode`` first.
        '''
        self.__encoding = encoding

    def set_connect_timeout(self, timeout):
        '''
        Defines a timeout for establishing a connection with a dubbo server.
        It should be noted that this timeout cannot usually exceed 75 seconds.
        defualt is ``10``
        '''
        self.__connect_timeout = timeout

    def set_read_timeout(self, timeout):
        '''
        Defines a timeout for reading a response expected from the dubbo server.
        defualt is ``10``
        '''
        self.__read_timeout = timeout

    def do(self, command):
        # 连接Telnet服务器
        try:
            tn = telnetlib.Telnet(host=self.host, port=self.port, timeout=self.__connect_timeout)
        except socket.error as err:
            print("[host:%s port:%s] %s" % (self.host, self.port, err))
            return

        # 触发doubble提示符
        tn.write(b'\n')

        # 执行命令
        tn.read_until(self.__finish, timeout=self.__read_timeout)
        tn.write(command + b'\n')

        # 获取结果
        data = b''
        while data.find(self.__finish) == -1:
            data = tn.read_very_eager()
        data = str(data, encoding=self.__encoding)
        data = data.split("\r\n")[:-1]
        try:
            data = json.loads(data[0], encoding=self.__encoding)
        except:
            data = data

        tn.close()  # tn.write('exit\n')

        return data

    def invoke(self, interface, method, param):
        cmd = "%s %s.%s(%s)" % ('invoke', interface, method, param)
        cmd = bytes(cmd, self.__encoding)
        return self.do1(cmd)

    #不获取结果
    def do1(self, command):
        # 连接Telnet服务器
        try:
            tn = telnetlib.Telnet(host=self.host, port=self.port, timeout=self.__connect_timeout)
        except socket.error as err:
            print("[host:%s port:%s] %s" % (self.host, self.port, err))
            return

        # 触发doubble提示符
        tn.write(b'\n')

        # 执行命令
        tn.read_until(self.__finish, timeout=self.__read_timeout)
        tn.write(command + b'\n')

        return

def connect(host, port):
    return dubbo(host, port)


from config import Config


#任务回调
def callBack(site,account,zt,callback_host='',callback_port=''):

    Host = callback_host or Config.DUBOO_HOST  # Doubble服务器IP
    Port = callback_port or Config.DUBOO_PORT  # Doubble服务端口

    # 初始化dubbo对象
    conn = dubbo(Host, Port)

    # 设置telnet连接超时时间
    conn.set_connect_timeout(60)

    # 设置dubbo服务返回响应的编码
    conn.set_encoding('gbk')

    interface = 'cn.ciccloud.finance.platform.service.IAfterSalesService'
    method = 'inputAccountForMysql'
    param = '{"systemId":"%s", "colletionId":"%s", "accId":"%s"}'%(site,account,zt)
    # param = '{"systemId":"%s","accId":"%s"}'%(site,zt)

    try:
        conn.invoke(interface, method, param)
    except Exception as e:
        from manage import sentry
        sentry.captureException()

    return


if __name__ == '__main__':
    Host = '192.168.1.58'  # Doubble服务器IP
    Port = 20882  # Doubble服务端口

    # 初始化dubbo对象
    conn = dubbo(Host, Port)

    # 设置telnet连接超时时间
    conn.set_connect_timeout(10)

    # 设置dubbo服务返回响应的编码
    conn.set_encoding('gbk')

    interface = 'cn.ciccloud.finance.platform.service.IAfterSalesService'
    method = 'inputAccount'
    param = '{"systemId":"kungeek", "colletionId":"m_23232", "accId":"099989898"}'
    print(conn.invoke(interface, method, param))

    command = 'ls -l'
    print(conn.do(command))
