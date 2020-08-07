# encoding =utf-8
"""
本文件提供作者自定义的文件读写相关功能。函数列表如下：
log
csv_import
csv_export
stime2filename
replaceAll
共计 87 行。
"""
import csv
import json
import os
import re
from os import listdir
from os.path import isfile

exec("import csv")


def log(*_, end="\n"):
    """
    输出日志，方便手工改输出，暂时先打印到屏幕上
    :param _:输出内容
    """
    print(*_, end=end)


def fast_import(file_name: str, ext="csv"):
    """
    导入文件。

    :thisday ext: 解码方式
    :thisday file_name: 导入文件名
    :return: 文件内容。
    """
    try:
        with open(file_name, "r")as f:
            # 本来可以用
            if ext == "csv":
                ret = list(csv.reader(f))
            elif ext == "json":
                ret = json.load(f)
            else:
                raise KeyError(f"未知文件格式：{ext}")
            return ret
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在：{file_name}")
    except KeyError:
        raise KeyError(f"未知文件格式：{ext}")
    except json.decoder.JSONDecodeError:
        # 有时候文件会被莫名清空，解析器会出错，给一个空的就行啦
        return {}


def fast_export(data, file_name, ext="csv"):
    """
    接受一个列表和输出文件目录，输出csv文件

    :param ext: 文件格式
    :param data: ext like [[line],[line]]
    :param file_name:
    :return: file_name
    """
    with open(file_name, "w+", newline="")as f:
        action = {"csv": "csv.writer(f).writerows(data)",
                  "json": "json.dump(data, f)"}
        exec(action.get(ext))
    return file_name


def stime2filename(file_time: str, file_type: str, dir_prefix: str = "", ext: str = ".csv"):
    """
    给定字符串格式时间，构建相应的csv文件名。
    stime2filename(2020070411,"fan") -> fans\fans2020070411.csv

    file_time: 时间前缀，数字字符串。
    file_type: 目标的文件类型（fan，cha，或cha_server）。
    config_dir: 默认的文件定位地址，默认为本文件目录。
    ext: 文件后缀名。默认为csv。
    """
    # fan文件特殊处理
    if file_type == "fan":
        fan_dir = os.path.join(dir_prefix, "fans\\")
        is_legal = lambda f: isfile(fan_dir + f) and re.match(rf"^fans{file_time}.*\.csv", f)
        legal_files = [f for f in listdir(fan_dir) if is_legal(f)]
        if not legal_files:
            raise FileNotFoundError(dir_prefix + f"fans{file_time}*.csv not exist.")
        file2size_dict = {f: os.stat(fan_dir + f).st_size for f in legal_files}
        ret = max(file2size_dict, key=file2size_dict.get)
        # 小文件也视作异常
        min_allowed_file_size = 1024
        if file2size_dict[ret] < min_allowed_file_size:
            raise FileNotFoundError
        return fan_dir + ret

    filename = {"fan_raw": f"fans{file_time}",
                "cha": fr"cha\cha{file_time}-1",
                "cha_server": fr"cha_server\cha{file_time}-1"}
    ret = os.path.join(dir_prefix, filename[file_type] + ext)
    return ret


def replaceAll(s: str, rule: dict):
    """约等于MMA的/.功能。"""
    for keys in rule:
        s = s.replace(keys, rule[keys])
    return s
