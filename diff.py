# encoding =utf-8
"""
做差相关函数。
共 81 行。
"""
from typing import List

import paths
from library.file import stime2filename, fast_export, fast_import, log
from library.time_process import onedayago, halfdayago, time_str_list, onehalfdayago


def fan_dict_data(fan_name: str, target_dir):
    """给出指定文件名的 fan 文件数据。"""
    datalist = fast_import(stime2filename(fan_name, "fan", target_dir))
    ret = {_[0]: dict(zip(datalist[0][1:], _[1:])) for _ in datalist[1:]}
    return ret


'''
以下将 today 的 fans > 10000 且 vidcount < 3 简称为「新大佬条件」
粉丝数 fans：默认 today - onedayago 做差，如 onedayago 无数据，与 halfdayago 做差并且数据乘二，若乘二后超过了 thisday 的数值
    则以 today 的数值代替。如两个数据点都没有数据，且满足「新大佬条件」时，
    前一天数据认为是零返回 today 的数据作为作差结果。点赞数投稿数等列的逻辑同上
播放量 vidview：默认 today - onedayago 做差，如 onedayago 无数据，与 halfdayago 做差并且数据不要乘二。
    如两个数据点都没有数据，且满足「新大佬条件」时，前一天数据认为是零返回 today 的数据作为作差结果。
    当作差成功但得结果为零时，将 today 和 1.5 天前 onehalfdayago 的结果作差取代之。
    若 onehalfdayago 无数据，则当满足「新大佬条件」时，返回 today 的数据作为作差结果，否则播放增量就填零
    （这个处理是因为B站每天才更新一次播放量数据，有一定概率 today，halfday，ondayago 爬到的都是相同的数据）
名字 name：输出 today 的名字到第 2 列，若跟 onedayago 相比有改名字则输出 onedayago 的名字到第 7 列，若未改名则第 7 列写 0
'''


def calu_vidview(new: int, old: int, old_old: int) -> List[int]:
    """
    参数分别为当天 一天或半天前 一天半前数据。
    若当天无数据 参数为零
    """
    # 新入站大佬说明前三个数据点都没有数据 也就是old 和 old_old 都是零
    # 不管new减去啥都是new自己
    ret: int = new - old if new - old else new - old_old if old_old else 0
    return [ret]


def point_diff(new, old, keys, halfday):
    old_and_news = [(int(new[_]), int(old.get(_, 0))) for _ in keys]
    ret = [min(n, (n - w) * halfday) for n, w in old_and_news]
    return ret


def line_diff(mid, new, old, old_old, halfday: int):
    """
    行做差。

    :param mid: 主键
    :param new: 新表
    :param old: 旧表（可能是半天之前或者一天之前）
    :param halfday: 半天情况下是2，否则是1
    :return: 做差结果
    """
    # 慢慢爬进来的情况，不予做差，否则当天会出现数据异常
    if not (old and old_old and old.get('charge') == -1) and (int(new["fans"]) < 10000 or int(new["vidview"]) > 3):
        return
    # 以下为正常人（含新大佬）
    # 1-3列:mid,名字 瞬时粉丝量
    ret_udata = [int(mid), new["name"], new["fans"]]
    # 4-5列：粉丝 视频数 的变化情况
    ret_fans = point_diff(new, old, ["fans", "vidcount"], halfday, )
    # 6列 播放数 要特殊处理
    ret_vidview: List[int] = calu_vidview(*[int(_.get("vidview", 0)) for _ in (new, old, old_old)])
    # 7列 旧名字 如果一样就是0
    ret_old_names = [0 if new["name"] == old.get("name", "") else old.get("name", "")]
    # 8-12列 关注 专栏阅读 等级 充电 点赞
    ret_other = point_diff(new, old, ['attention', 'zview', 'level', 'charge', 'likes'], halfday)

    ret: List[List] = ret_udata + ret_fans + ret_vidview + ret_old_names + ret_other
    return ret


def cha(today: dict, halfDago: dict, oneDago: dict, onehalfDago: dict):
    """
    对 today 的数据进行做差。默认与 onedayago 做差，
    如 onedayago 无数据，与 halfdayago 做差并且数据乘二。
    如两个数据点都没有数据，认为是新入站用户，前一天数据认为是零。

    :param today: 当前数据
    :param oneDago: 半天前数据
    :param halfDago:，一天前数据
    """
    ret = []
    for mid in today.keys():
        new = today[mid]
        # 若无数据，则给一个None
        old = oneDago.get(mid, halfDago.get(mid, {}))
        # 没有数据那只能认为是零了
        # old_vid_view = int(onehalfDago.get(mid, {"vidview": 0})["vidview"])
        old_old = onehalfDago.get(mid, {})
        line = line_diff(mid, new, old, old_old, halfday=(2 if (old == halfDago.get(mid)) else 1))
        if line:
            ret.append(line)
    ret.sort()
    return ret


def export_data(datalist: List[dict], i_time) -> List[List]:
    """
    :@param datalist:数据列表 实际上只需要最后4项
    :@param i_time:字符串时间
    """
    # 表头
    # mid, today_name, fans2020080611, fans, vidcount, vidview, oldname, attention, zview, level,charge, likes
    export_head = fast_import(stime2filename(i_time, "fan", paths.serv))[0][:10]
    export_head.insert(1, "today_name")
    export_head.insert(2, stime2filename(i_time, "fan_raw", ext=""))
    export_head[6] = "old_name"

    # export_body = cha(datalist[-1], datalist[-2], datalist[-3], datalist[-4])
    # 需要当天数据，一天前数据，备用的半天前数据，用来计算的一天半前数据
    export_body = cha(*datalist[:-5:-1])
    export = [export_head] + export_body
    return export


def diff(t_start, t_end, target_dir=paths.serv):
    """
    给定起止时间，每半天计算一个差文件

    :param t_start: 开始时间，字符串格式
    :param t_end: 结束时间，字符串格式
    :param target_dir: 输出路径，cha 文件夹的上级目录
    """
    log(f" 正在做差：\n\t 起始时间：{t_start}\n\t 终止时间：{t_end}\n\t 输出目录：{target_dir}")
    # 初始数据 遍历
    datalist = [fan_dict_data(_(t_start), target_dir)
                for _ in (onehalfdayago, onedayago, halfdayago)]
    time_list = time_str_list(t_start, t_end)
    # 对于每个时间点分别进行做差
    for i_time in time_list:
        datalist.append(fan_dict_data(i_time, target_dir))
        export = export_data(datalist, i_time)
        export_dir = stime2filename(i_time, "cha", target_dir)
        fast_export(export, export_dir)
        print(f"export file at {export_dir}")


if __name__ == "__main__":
    """
    参考运行时间（基准=i7-8750@3.7GHz，输出存放于移动硬盘）
    1个数据点（即刻）->4-5s
    14-15个数据点（一周）->41-44s
    约60个数据点（一月）->169-172s
    """
    diff("2020081211", "2020081211",
         r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp""\\")

    import time

    print(time.process_time())
