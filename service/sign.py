#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/5
# @Author : chaocai


# 签到入口
import datetime
import json

from service import util, config


# 签到入口
async def sign(login_info, session):
    if login_info.site == 'lightnovel':
        await lightnovel_sign(login_info, session)
    if login_info.site == 'masiro':
        await masiro_sign(login_info, session)


# 真白萌签到
async def masiro_sign(login_info, session):
    # 登录签到
    print('%s真白萌账号%s开始签到...' % (datetime.datetime.now(), login_info.username))
    sign_url = 'https://masiro.me/admin/dailySignIn'
    await util.http_get(sign_url, util.build_headers(login_info), None, '连接已断开，重试中... ', session)
    print('每日登录签到成功！')
    # 祈愿池
    if config.read('is_wish'):
        print('真白萌账号%s开始祈愿...' % login_info.username)
        wish_url = 'https://masiro.me/admin/gachiyaWishingPond'
        wish_param = {'wp_id': 1, 'cost': 10}
        text = await util.http_post(wish_url, util.build_headers(login_info), wish_param, None,
                                    '连接已断开，重试中... ', False, session)
        if text:
            print(json.loads(text)['msg'])
        else:
            print('祈愿失败！')


# 轻国签到
async def lightnovel_sign(login_info, session):
    # 登录签到
    print('%s轻国账号%s开始签到...' % (datetime.datetime.now(), login_info.username))
    sign_url = 'https://api.lightnovel.us/api/task/complete'
    param_str = '{"platform":"android","client":"app","sign":"","ver_name":"0.11.50","ver_code":190,' \
                '"d":{"id":8,"security_key":"' + login_info.token + '"},"gz":1}'
    text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(param_str), None,
                                '连接已断开，重试中... ', True, session)
    res = util.unzip(text)['code']
    lightnovel_print_res(res, '每日登录签到成功！', '今天已经签到过了')
    # 任务
    await lightnovel_task(login_info, session)


# 轻国任务
async def lightnovel_task(login_info, session):
    sign_url = 'https://api.lightnovel.us/api/task/complete'
    sign_param = '{"platform":"android","client":"app","sign":"","ver_name":"0.11.50","ver_code":190,' \
                 '"d":{"id":%s,"security_key":"' + login_info.token + '"},"gz":1}'
    # 阅读
    print('轻国账号%s开始进行阅读任务...' % login_info.username)
    read_url = 'https://api.lightnovel.us/api/history/add-history'
    read_param = '{"platform":"android","client":"app","sign":"","ver_name":"0.11.50","ver_code":190,' \
                 '"d":{"fid":2408,"class":2,"security_key":"' + login_info.token + '"},"gz":1}'
    await util.http_post(read_url, util.build_headers(login_info), json.loads(read_param), None,
                         '连接已断开，重试中... ', True, session)
    read_text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(sign_param % '1'), None,
                                     '连接已断开，重试中... ', True, session)
    read_res = util.unzip(read_text)['code']
    lightnovel_print_res(read_res, '阅读任务完成！', '阅读任务失败！')
    # 收藏
    print('轻国账号%s开始进行收藏任务...' % login_info.username)
    collection_url = 'https://api.lightnovel.us/api/history/add-collection'
    collection_param = '{"platform":"android","client":"app","sign":"","ver_name":"0.11.50","ver_code":190,' \
                       '"d":{"fid":1123305,"class":1,"security_key":"' + login_info.token + '"},"gz":1}'
    await util.http_post(collection_url, util.build_headers(login_info), json.loads(collection_param), None,
                         '连接已断开，重试中... ', True, session)
    collection_text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(sign_param % '2'), None,
                                           '连接已断开，重试中... ', True, session)
    collection_res = util.unzip(collection_text)['code']
    lightnovel_print_res(collection_res, '收藏任务完成！', '收藏任务失败！')
    # 点赞
    print('轻国账号%s开始进行点赞任务...' % login_info.username)
    like_url = 'https://api.lightnovel.us/api/article/like'
    like_param = '{"platform":"android","client":"app","sign":"","ver_name":"0.11.50","ver_code":190,' \
                 '"d":{"aid":1123305,"security_key":"' + login_info.token + '"},"gz":1}'
    await util.http_post(like_url, util.build_headers(login_info), json.loads(like_param), None,
                         '连接已断开，重试中... ', True, session)
    like_text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(sign_param % '3'), None,
                                     '连接已断开，重试中... ', True, session)
    like_res = util.unzip(like_text)['code']
    lightnovel_print_res(like_res, '点赞任务完成！', '点赞任务失败！')
    # 分享
    print('轻国账号%s开始进行分享任务...' % login_info.username)
    share_text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(sign_param % '5'), None,
                                      '连接已断开，重试中... ', True, session)
    share_res = util.unzip(share_text)['code']
    lightnovel_print_res(share_res, '分享任务完成！', '分享任务失败！')
    # 投币
    print('轻国账号%s开始进行投币任务...' % login_info.username)
    pay_url = 'https://api.lightnovel.us/api/coin/use'
    pay_param = '{"platform":"android","client":"app","sign":"","ver_name":"0.11.50","ver_code":190,' \
                '"d":{"goods_id":2,"params":1123305,"price":1,"number":10,"total_price":10,"security_key":"' + login_info.token + '"},"gz":1}'
    await util.http_post(pay_url, util.build_headers(login_info), json.loads(pay_param), None,
                         '连接已断开，重试中... ', True, session)
    pay_text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(sign_param % '6'), None,
                                    '连接已断开，重试中... ', True, session)
    pay_res = util.unzip(pay_text)['code']
    lightnovel_print_res(pay_res, '投币任务完成！', '投币任务失败！')
    # 全部完成
    print('轻国账号%s开始进行最终任务...' % login_info.username)
    final_text = await util.http_post(sign_url, util.build_headers(login_info), json.loads(sign_param % '7'), None,
                                      '连接已断开，重试中... ', True, session)
    final_res = util.unzip(final_text)['code']
    lightnovel_print_res(final_res, '全部任务完成！', '最终任务失败！')


# 轻国打印签到结果
def lightnovel_print_res(res, success_info, fail_info):
    if res == 0:
        print(success_info)
    else:
        print(fail_info)
