#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/5/20
# @Author : chaocai
import json

from lxml import html

from service import config, util, log


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
    # 轻国uid
    uid: None
    # hash 百合会需要
    hash: None

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
    if login_info.site == 'yuri':
        # 百合会获取hash
        await discuz_get_hash(login_info, session)
    login_param = build_login_param(login_info)
    login_headers = build_login_headers(login_info)
    if login_info.site == 'yuri':
        login_info.url = login_info.url % login_info.hash['loginhash']
    res = await util.http_post(login_info.url, login_headers, login_param, None, '登录失败！',
                               True if login_info.site == 'lightnovel' else False, session)
    if login_info.site == 'lightnovel':
        # 轻国设置token
        login_info.token = json.loads(res)['data']['security_key']
        login_info.uid = json.loads(res)['data']['uid']
    log.info('账号%s登录成功！' % login_info.username)


# discuz论坛获取hash
async def discuz_get_hash(login_info, session):
    headers = config.read('headers')
    res = await util.http_get('https://bbs.yamibo.com/member.php?mod=logging&action=login', headers,
                              None, '获取登录hash失败！', session)
    page_body = html.fromstring(res)
    login_info.hash = {'formhash': str(page_body.xpath('//input[@name=\'formhash\']/@value')[0]),
                       'loginhash': str(page_body.xpath('//form[@name=\'login\']/@action')[0])}


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
    if login_info.site == 'yuri':
        return {
            'formhash': login_info.hash['formhash'],
            'referer': 'https://bbs.yamibo.com/forum-55-2.html',
            'username': login_info.username,
            'password': login_info.password,
            'questionid': '0',
            'answer': '',
            'cookietime': '2592000'
        }
