# 好颜色文件的路径
import json
import os
import re

import numpy as np
import requests

import paths
from download_header import download_header as download
from library.file import fast_import, log

good_color_dir = paths.byk + "data\\好颜色.csv"
good_color = dict(fast_import(good_color_dir))

# 注销改名文件数据
logoff_pattern = "账号[已]?注销[0-9]*|[0-9]+_bili|bili_[0-9]+"
with open(paths.logoff_dir, encoding='UTF-8') as f:
    logoff = json.load(f)

# 输出目标路径
export_dir = paths.anime

# api地址
api_url = "https://api.bilibili.com/x/web-interface/card?mid="

# blacklist
blacklist = ["吴织亚切大忽悠"]

dheader = download(good_color, export_dir)
download_header = dheader.download_header


def download_header_mma(uid, face_link):
    """已弃用"""
    command = fr"wolframscript -file headpic.wls {uid} {face_link} {export_dir}"
    with os.popen(command, 'r') as f:
        color = f.read().replace("\n", "")
    if uid in good_color:
        color = good_color[uid]
    return color


def crawl(up_data, index):
    """
    爬取单个用户的名称并且计算颜色

    @param up_data:插值完成后某up的数据
    @param index: 序号 只是为了输出数值好看而已
    @return: 输出文件中up对应数据的那一列（行）
    """
    # userdata
    uid = up_data[0]
    log(f"\t{index:<3}:正在处理{uid:<8}", end="" if index % 5 else "\n")
    udata = up_data[1:]
    try:
        # 主要处理过程，前后杂事多，单独写一个函数
        ret_s = get_ret_s(udata, uid)
        # 字符串数字转数值，收尾格式化
        ret = np.array(ret_s).tolist()
    # 超时处理
    except requests.exceptions.ReadTimeout:
        log(f"访问api超时。用户uid：{uid}")
        ret = [uid, 0, 0] + udata
    return ret


def get_ret_s(udata, uid):
    # 读api获取用户信息
    content = get_content(uid)
    # up名称，要做比较多的判断处理 单独写函数
    name = get_name(content)
    # 爬取头像 计算颜色
    face_link = content["data"]["card"]["face"]
    color = download_header(uid, face_link)

    ret_s = [uid, name, color] + udata
    return ret_s


def get_content(uid):
    url = api_url + uid
    response = requests.get(url, timeout=10)
    content = json.loads(response.content)
    return content


def get_name(content):
    name = content["data"]["card"]["name"]
    uid = content["data"]["card"]["mid"]
    if name in blacklist:
        name = ""
    elif uid in logoff:
        name += f"（原：{logoff[uid]}）"
    elif re.search(logoff_pattern, name) is not None:
        log(f"  新发现注销帐号：{name}，用户uid:{uid}")
    return name


def headpic(inter_data):
    """
    对插值后的数据爬取up头像，计算指定颜色。
    :param inter_data: 插值后的数据，二维表格。
    :return: 最后需要的总表“data.csv”,zip object
    """
    # 表头
    head = inter_data[0]
    ret_head = [head[0], "", ""] + head[1:]
    # 表体
    ret_body = [crawl(up_data, index) for index, up_data in enumerate(inter_data[1:], 1)]
    print()  # 换行
    # 转置
    ret = zip(ret_head, *ret_body)
    return ret


if __name__ == "__main__":
    retttttt = download_header(29762504, "http://i0.hdslb.com/bfs/face/4f6f5fddba459ae2b2ecc913ff9375db7c484eb4.jpg")
    print(retttttt)
