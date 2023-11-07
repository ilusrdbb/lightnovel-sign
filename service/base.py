#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/5/20
# @Author : chaocai
import aiohttp

from service import login, config, sign


async def start_sign(site):
    if site == 'all':
        await _start_sign('lightnovel')
    else:
        await _start_sign(site)


# 开始签到
async def _start_sign(site):
    login_list = config.read('login_info')[site]
    if login_list:
        for username_pwd in login_list:
            jar = aiohttp.CookieJar(unsafe=True)
            conn = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=conn, trust_env=True, cookie_jar=jar) as session:
                # 登录
                login_info = login.Login(site, username_pwd['username'], username_pwd['password'])
                await login.login(login_info, session)
                # 签到
                await sign.sign(login_info, session)

