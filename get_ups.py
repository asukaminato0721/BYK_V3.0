# encoding =utf-8
import paths
from library.file import fast_export, stime2filename, fast_import
from library.time_process import time_str_list


def select_from_a_file(file_data, top_count):
    """从单个文件中搜索前若干名"""
    # 第四列：粉丝量，对应这里的key选择x的第四列（x[3]）
    # 要做粉丝榜以外的改这里可以很方便的处理
    # 我不知道这里到底应该是大于还是小于 如果输出结果不对的话改这里
    sorted_data = sorted(file_data[1:], key=lambda x: int(x[3]), reverse=top_count > 0)[:top_count]
    concerned_updata = sorted_data[:abs(top_count)]
    ups = {_[0] for _ in concerned_updata}
    return ups


def select_from_files(start, end, gainlost, cha_dir=paths.serv):
    """
    :param start,end:起止时间
    :param gainlost: 涨粉还是掉粉
    :param gainlost: 涨粉为True，否则是False
    :return:ups_ :List
    """
    top_count = 30 if gainlost == "gain" else -30
    filenames = time_str_list(start, end)
    # debug = True
    # if debug:
    #     filenames = time_str_list(t_start, "2020080411")
    file_data = [fast_import(stime2filename(ftime, "cha", dir_prefix=cha_dir)) for ftime in filenames]
    # ups =reduce(lambda x, y:x|y,[select_from_a_file(file, top_count=top_count) for file in file_data])
    ups = set.union(*[select_from_a_file(file, top_count=top_count) for file in file_data])
    fast_export([ups], "temp/ups.csv", "csv")
    return ups


if __name__ == "__main__":
    default_absolute_dir = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp"
    cha_dir = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp"
    select_from_files("2020070123", "2020073011", False, cha_dir)
