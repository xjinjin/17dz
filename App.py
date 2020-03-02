# -*- coding:utf-8 -*-

from flask import Flask

from config import Config

app = Flask(__name__)
# 配置
app.config.from_object(Config)  # 加载配置 (字符串，文件名，类)
