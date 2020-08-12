# 好颜色文件的路径
import json
import os
import re

import numpy as np
import requests

from library.file import fast_import, log

# TODO 改 paths

good_color_dir = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\data\好颜色.csv"
good_color = dict(fast_import(good_color_dir))

# 注销改名文件的路径
logoff_dir = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\data\logoff.json"
logoff_pattern = "账号[已]?注销[0-9]*|[0-9]+_bili"
with open(logoff_dir) as f:
    logoff = json.load(f)

# 输出目标路径
export_dir = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\amine"

# api地址
api_url = "https://api.bilibili.com/x/web-interface/card?mid="

# blacklist
blacklist = ["吴织亚切大忽悠"]


def download_header(uid, face_link):
    command = fr"wolframscript -file headpic.wls {uid} {face_link}"
    with os.popen(command, 'r') as f:
        color = f.read().replace("\n", "")
    if uid in good_color:
        color = good_color[uid]
    return color


def crawl(up_data, index):
    """
    爬取用户名 计算颜色

    :param up_data:插值完成后某up的数据
    :return: 输出文件中up的全部数据
    """
    # uid
    uid = up_data[0]
    log(f"{index}:正在处理{uid}", end="\t" if index % 5 else "\n")
    udata = up_data[1:]
    # 超时处理
    try:
        url = api_url + uid
        response = requests.get(url, timeout=10)
    except requests.exceptions.ReadTimeout:
        log(f"访问api超时。用户uid：{uid}")
        ret = [uid, 0, 0] + udata
        return ret
    content = json.loads(response.content)
    # up名称
    name = content["data"]["card"]["name"]
    if uid in logoff:
        name += f"（原：{logoff[uid]}）"
    elif name in blacklist:
        name = ""
    elif re.search(logoff_pattern, name) is not None:
        log(f"！！！新发现注销帐号：{name}，用户uid:{uid}")
    # up 爬取头像并且计算颜色
    face_link = content["data"]["card"]["face"]
    color = download_header(uid, face_link)

    # 字符串数字转数值
    ret_s = [uid, name, color] + udata
    ret = np.array(ret_s).tolist()
    return ret


def headpic(inter_data):
    """
    对插值后的数据爬取up头像，计算指定颜色。
    :param inter_data: 插值后的数据，二维表格。
    :return: 最后需要的总表“data.csv”,zip object
    """
    # 表头
    head = inter_data[0]
    ret_head = [head[0], "", ""] + head[1:]
    ret_body = [crawl(up_data, index) for up_data, index in zip(inter_data[1:], range(1, len(inter_data)))]
    # transpose
    ret = zip(ret_head, *ret_body)
    return ret


if __name__ == "__main__":
    ret = download_header(29762504, "http://i0.hdslb.com/bfs/face/4f6f5fddba459ae2b2ecc913ff9375db7c484eb4.jpg")
    print(ret)
