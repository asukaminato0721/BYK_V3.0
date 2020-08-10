# encoding =utf-8
"""
做差相关函数。
共81行。
"""
from library.file import stime2filename, fast_export, fast_import
from library.time_process import onedayago, halfdayago, time_str_list


def fan_dict_data(fan_name: str, target_dir):
    """
    给出指定文件名的fan文件数据。
    """
    datalist = fast_import(stime2filename(fan_name, "fan", target_dir))
    ret = {_[0]: _[1:] for _ in datalist[1:]}
    return ret


def line_diff(key_, new, old, is_halfday: bool):
    """
    行做差。

    :param key_: 主键
    :param new: 新表
    :param old: 旧表
    :param is_halfday: 是否是半天的，如果是的话结果翻倍。
    :return: 做差结果
    """
    ret_head = [int(key_)]  # 确保后面排序的时候是按照数字排序的
    ret_udata = [new[3], new[0]]
    ret_fans = [(int(_[1]) - int(_[0])) * (2 if is_halfday else 1) for _ in zip(old[:3], new[:3])]
    ret_other = [(int(_[1]) - int(_[0])) * (2 if is_halfday else 1) for _ in zip(old[4:9], new[4:9])]
    ret = ret_head + ret_udata + ret_fans + [0] + ret_other
    return ret


def cha(thisday: dict, oneDago: dict, halfDago: dict):
    """
    对 thisday 的数据进行做差。默认与 onedayago 做差，
    如onedayago无数据，与 halfdayago 做差并且数据乘二。
    如两个数据点都没有数据，认为是新入站用户，前一天数据认为是零。

    :param thisday:当前数据
    :param oneDago:半天前数据
    :param halfDago:，一天前数据
    """
    ret = []
    for mid in thisday.keys():
        new = thisday[mid]
        old = oneDago.get(mid, halfDago.get(mid, [0] * len(new)))
        line = line_diff(mid, new, old, old == halfDago.get(mid))
        ret.append(line)
    ret.sort()
    return ret


def diff(t_start, t_end, target_dir):
    """
    给定起止时间，每半天计算一个差文件

    :thisday t_start: 开始时间，字符串格式
    :thisday t_end: 结束时间，字符串格式
    :thisday target_dir: 输出路径，cha文件夹的上级目录
    :return:
    """
    print(f"正在做差：\n\t起始时间：{t_start}\n\t终止时间：{t_end}\n\t输出目录：{target_dir}")
    # 初始数据
    datalist = [fan_dict_data(onedayago(t_start), target_dir), fan_dict_data(halfdayago(t_start), target_dir)]
    # 遍历
    time_list = time_str_list(t_start, t_end)
    for i_time in time_list:
        datalist.append(fan_dict_data(i_time, target_dir))
        # 表头
        export_head = fast_import(stime2filename(i_time, "fan", target_dir))[0][:10]
        export_head.insert(1, "name")
        export_head.insert(2, stime2filename(i_time, "fan_raw", ext=""))

        export_body = cha(datalist[-1], datalist[-3], datalist[-2])
        export = [export_head] + export_body
        export_dir = stime2filename(i_time, "cha", target_dir)
        fast_export(export, export_dir)
        print(f"export file at {export_dir}")


if __name__ == "__main__":
    diff("2020080611", "2020080611", r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp""\\")

    import time

    print(time.process_time())
