#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/5/20
# @Author : chaocai
import json

from lxml import html
from service import config, util


class Login:
    # 站点
    site: None
    # 地址
    url: None
    # 用户名
    username: None
    # 密码
    password: None
    # token
    token: None

    # 初始化
    def __init__(self, site, username, password):
        self.site = site
        self.username = username
        self.password = password
        self.url = config.read('url_config')[site]


# 真白萌获取token
async def masiro_get_token(login_info, session):
    res = await util.http_get('https://masiro.me/admin/auth/login', config.read('headers'),
                              None, '获取token失败！', session)
    page_body = html.fromstring(res)
    login_info.token = str(page_body.xpath('//input[@class=\'csrf\']/@value')[0])


# 登录入口
async def login(login_info, session):
    if login_info.site == 'masiro':
        # 真白萌设置token
        await masiro_get_token(login_info, session)
    login_param = build_login_param(login_info)
    login_headers = build_login_headers(login_info)
    res = await util.http_post(login_info.url, login_headers, login_param, None, '登录失败！',
                               True if login_info.site == 'lightnovel' else False, session)
    if login_info.site == 'lightnovel':
        # 轻国设置token
        login_info.token = json.loads(res)['data']['security_key']
    print('账号%s登录成功！' % login_info.username)


# 构造请求头
def build_login_headers(login_info):
    headers = config.read('headers')
    if login_info.site == 'masiro':
        headers['x-csrf-token'] = login_info.token
        headers['x-requested-with'] = 'XMLHttpRequest'
    if login_info.site == 'lightnovel':
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        headers['Origin'] = 'https://www.lightnovel.us'
        headers['Referer'] = 'https://www.lightnovel.us/cn/'
    return headers


# 构造传参
def build_login_param(login_info):
    if login_info.site == 'masiro':
        return {
            'username': login_info.username,
            'password': login_info.password,
            'remember': '1',
            '_token': login_info.token
        }
    if login_info.site == 'lightnovel':
        return {
            'client': 'web',
            'd': {
                'username': login_info.username,
                'password': login_info.password,
            },
            'gz': 0,
            'is_encrypted': 0,
            'platform': 'pc',
            'sign': ''
        }
