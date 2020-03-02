#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5


class RClient(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_params = {
            'username': self.username,
            'password': self.password,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://aiapi.c2567.com/api/create', data=params, files=files, headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://aiapi.c2567.com/api/reporterror', data=params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    rc = RClient('cicjust', 'JYcxys@3030')

    im = open('full_img.png', 'rb').read()

    print (rc.rk_create(im, 3000))

