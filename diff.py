# encoding =utf-8
"""
做差相关函数。
共 81 行。
"""
import paths
from library.file import stime2filename, fast_export, fast_import
from library.time_process import onedayago, halfdayago, time_str_list, onehalfdayago


def fan_dict_data(fan_name: str, target_dir):
    """给出指定文件名的 fan 文件数据。"""
    datalist = fast_import(stime2filename(fan_name, "fan", target_dir))
    ret = {_[0]: dict(zip(datalist[0][1:], _[1:])) for _ in datalist[1:]}
    return ret


'''
粉丝数 fans：默认 today - onedayago 做差，如 onedayago 无数据，与 halfdayago 做差并且数据乘二，若乘二后超过了 thisday 的数值
    则以 today 的数值代替。如两个数据点都没有数据，且 today 的 fans > 10000，认为是新入站用户，前一天数据认为是零返回 today 的数据作为作差结果 点赞数投稿数等列的逻辑同上 
播放量 vidview：逻辑同上，并且当作差得结果为零时，将 today 和1.5天前 onehalfdayago 的结果作差取代之
    （这个处理是因为B站每天才更新一次播放量数据，有一定概率 today，halfday，ondayago 爬到的都是相同的数据）
名字 name：输出 today 的名字到第 2 列，若跟 onedayago 相比有改名字则输出 onedayago 的名字到第 7 列，若未改名则第 7 列写 0
'''


def line_diff(mid, new, old, old_vid_view, halfday: int):
    """
    行做差。

    :param mid: 主键
    :param new: 新表
    :param old: 旧表（可能是半天之前或者一天之前）
    :param halfday: 半天情况下是2，否则是1
    :return: 做差结果
    """
    # 慢慢爬进来的情况，不予做差，否则当天会出现数据异常
    if old is None:
        if int(new["fans"]) < 10000:
            return
        else:
            old = {}
    # 以下为正常人
    # 1-3列:mid,名字 瞬时粉丝量
    ret_udata = [int(mid), new["name"], new["fans"]]
    # 4-5列：粉丝 视频数 的变化情况
    ret_fans = [min(n, (n - w) * halfday)
                for n, w in [(int(new[_]), int(old[_]))
                             for _ in ["fans", "vidcount"]]]
    # 6列 播放数 要特殊处理
    ret_vidview = [min(n, (n - w if n - w > 0 else n - old_vid_view) * halfday)
                   for n, w in [(int(new[_]), int(old.get(_)))
                                for _ in ["vidview"]]]
    # 7列 旧名字 如果一样就是0
    ret_old_names = [0 if new["name"] == old["name"] else old["name"]]
    # 8-12列 关注 专栏阅读 等级 充电 点赞
    ret_other = [min(n, (n - w) * halfday)
                 for n, w in [(int(new[_]), int(old[_]))
                              for _ in ['attention', 'zview', 'level', 'charge', 'likes']]]

    ret = ret_udata + ret_fans + ret_vidview + ret_old_names + ret_other
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
        old = oneDago.get(mid, halfDago.get(mid, None))
        # 没有数据那只能认为是零了
        old_vid_view = int(onehalfDago.get(mid, {"vidview": 0})["vidview"])
        line = line_diff(mid, new, old, old_vid_view, halfday=(2 if (old == halfDago.get(mid)) else 1))
        if line:
            ret.append(line)
    ret.sort()
    return ret


def diff(t_start, t_end, target_dir=paths.serv):
    """
    给定起止时间，每半天计算一个差文件

    :param t_start: 开始时间，字符串格式
    :param t_end: 结束时间，字符串格式
    :param target_dir: 输出路径，cha 文件夹的上级目录
    """
    print(f" 正在做差：\n\t 起始时间：{t_start}\n\t 终止时间：{t_end}\n\t 输出目录：{target_dir}")
    # 初始数据
    datalist = [fan_dict_data(_(t_start), target_dir) for _ in (onehalfdayago, onedayago, halfdayago)]
    # 遍历
    time_list = time_str_list(t_start, t_end)
    # 对于每个时间点分别进行做差
    for i_time in time_list:
        datalist.append(fan_dict_data(i_time, target_dir))
        # 表头
        export_head = fast_import(stime2filename(i_time, "fan", target_dir))[0][:10]
        export_head.insert(1, "today_name")
        export_head.insert(2, stime2filename(i_time, "fan_raw", ext=""))
        export_head[6] = "old_name"
        # mid, today_name, fans2020080611, fans, vidcount, vidview, oldname, attention, zview, level,charge, likes

        # export_body = cha(datalist[-1], datalist[-2], datalist[-3], datalist[-4])
        export_body = cha(*datalist[:-5:-1])
        # 需要当天数据，一天前数据，备用的半天前数据，用来计算的一天半前数据
        export = [export_head] + export_body
        export_dir = stime2filename(i_time, "cha", target_dir)
        fast_export(export, export_dir)
        print(f"export file at {export_dir}")


if __name__ == "__main__":
    diff("2020081123", "2020081123", r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp""\\")

    import time

    print(time.process_time())
