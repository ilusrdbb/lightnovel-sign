#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/5/20
# @Author : chaocai
import base64
import json
import zlib

from tenacity import retry, stop_after_attempt

from service import config, log


# 通用get请求
@retry(stop=stop_after_attempt(3))
async def http_get(url, headers, fail_info, session):
    text = None
    proxy = config.read('proxy_url') if config.read('proxy_url') else None
    try:
        response = await session.get(url=url, headers=headers, proxy=proxy,
                                     timeout=config.read('time_out'))
        if not response.status == 200:
            raise Exception(fail_info) if fail_info else Exception()
    except Exception as e:
        if fail_info:
            log.info(fail_info)
        raise e
    return text


# 通用post请求
@retry(stop=stop_after_attempt(3))
async def http_post(url, headers, param, success_info, fail_info, is_json, session):
    proxy = config.read('proxy_url') if config.read('proxy_url') else None
    try:
        if is_json:
            response = await session.post(url=url, headers=headers, proxy=proxy,
                                          json=param, timeout=config.read('time_out'))
        else:
            response = await session.post(url=url, headers=headers, proxy=proxy,
                                          data=param, timeout=config.read('time_out'))
        if not response.status == 200:
            raise Exception(fail_info) if fail_info else Exception()
        text = await response.text()
        if success_info:
            log.info(success_info)
    except Exception as e:
        if fail_info:
            log.info(fail_info)
        raise e
    return text


# 通用构造请求头
def build_headers(login_info):
    headers = config.read('headers')
    if login_info.site == 'lightnovel':
        headers = {}
        headers['user-agent'] = 'Dart/2.10 (dart:io)'
        headers['content-type'] = 'application/json; charset=UTF-8'
        headers['accept-encoding'] = 'gzip'
        headers['host'] = 'api.lightnovel.fun'
    return headers


# gzip解压
def unzip(str):
    b = base64.b64decode(str)
    s = zlib.decompress(b).decode()
    return json.loads(s)