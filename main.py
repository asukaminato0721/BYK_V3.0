# encoding =utf-8
import os
import time

import cfg
import dailydata
import fdata
import get_ups as ups
import interpolate
from diff import diff
# global variable
from headpic import headpic
from library.file import fast_export, log

default_absolute_dir = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake"
config_dir = "D:\\OneDrive\\LiWorkshop\\BYK_V3.0\\"
cha_dir = os.path.join(default_absolute_dir, "temp")
ups_dir = "temp/ups.csv"
raw_dir = "temp/data_raw"
inter_dir = "temp/data_yuedu.csv"
data_dir = r"amine\data.csv"

# load config
config = cfg.Config(config_dir)

fan_type = input("选择：涨粉=gain/掉粉=lost \n ")
config.gainlost(fan_type)

duration_type = int(input("选择持续时间：周榜=0/月榜=对应月份 \n "))
config.month(duration_type)

# diff(elective,get cha files)
need_diff = input("是否做差？0=已有/1=要\n")
if need_diff == "1":
    log("开始做差")
    diff(config.t_start(), config.t_end(), cha_dir)
    log("做差完成")
else:
    log("跳过做差")

# search(get ups_)
log("开始搜索up名单")
ups = ups.select_from_files(config.t_start(), config.t_end(), config.gainlost(), cha_dir)
fast_export([[int(_) for _ in ups]], ups_dir, "csv")
log("输出up名单成功")

# video_list(elective,get amine/fdata)
if config.gainlost() == "gain" and config.month():
    log("开始获取fdata信息")
    months = {config.t_start()[:6], time.strftime("%Y%m")}
    fdata.export_fdata(ups, months)
    log("fdata信息输出成功")

# gather(get data-raw)
log("开始采集涨掉粉数据")
data_raw = dailydata.daysdata(*config.times(), ups, config.gainlost())
fast_export(data_raw, r"temp/data-raw.csv")
log("采集涨掉粉数据成功")

# interpolate (toget data-yuedu)
log("开始插值")
inter = interpolate.table_interpolate(data_raw, config.gainlost())
fast_export(inter, inter_dir)
log("插值成功")

# crawl headpic(get amine/data)
log("开始获取头像信息")
data_final = headpic(inter)
fast_export(data_final, data_dir)
log("头像信息获取成功")

# generate config.csv
log("开始生成config.csv")
cfg.generate_config(config.gainlost(), 0 if config.gainlost() == "gain" else config.month(), len(ups))
log("config.csv生成成功")

# ending
log("工作成功，保存配置文件")
