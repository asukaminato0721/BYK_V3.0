# encoding =utf-8
import time

import cfg
import dailydata
import fdata
import get_ups as ups
import interpolate
import paths
from cfg import config
from diff import diff
# global variable
from headpic import headpic
from library.file import fast_export, log

default_absolute_dir = paths.serv

# 几个中间文件 不影响运行
ups_dir = "temp/ups.csv"
raw_dir = "temp/data_raw"
inter_dir = "temp/data_yuedu.csv"
data_dir = r"anime/data.csv"

# load config
# config = cfg.Config()


fan_type = input("选择：涨粉=gain/掉粉=lost \n ")
config.gainlost(fan_type)

duration_type = int(input("选择持续时间：周榜=0/月榜=对应月份 \n "))
config.month(duration_type)

# diff(elective, get cha files)
mode = input("是否做差？skip(0)=跳过；force(1)=强制；其它=自动\n")
if mode in ("skip", "0"):
    log("跳过做差")
else:
    log("开始做差")
    diff(config.t_start(), config.t_end(), force=mode in ("force", "1"))
    log("做差完成")

# search(get ups_)
log("开始搜索up名单")
ups = ups.select_from_files(config.t_start(), config.t_end(), config.gainlost())
fast_export([[int(_) for _ in ups]], ups_dir, "csv")
log(f"输出up名单成功 共计{len(ups)}位")

# video_list(elective,get anime/fdata)
if config.gainlost() == "gain" and config.month():
    log("开始获取fdata信息")
    months = {config.t_start()[:6], time.strftime("%Y%m")}
    fdata.export_fdata(ups, months)
    log("fdata信息输出成功")

# gather(get data-raw)
log("开始采集涨掉粉数据")
data_raw = dailydata.daysdata(ups,config)
fast_export(data_raw, r"temp/data-raw.csv")
log("采集涨掉粉数据成功")

# interpolate (toget data-yuedu)
log("开始插值")
inter = interpolate.table_interpolate(data_raw)
fast_export(inter, inter_dir)
log("插值成功")

# crawl headpic(get anime/data)
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

# TODO
# 保存压缩包
print(time.process_time())
