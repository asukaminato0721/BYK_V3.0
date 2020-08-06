# encoding =utf-8
"""
本文件提供作者自定义的时间处理相关功能。函数列表如下：
str2tuple
str2unix
unix2str
halfdayago
onedayago
oneweekago
time_str_list
smart_choice_time
smart_choice_startend
共计91行。
"""
import time
from calendar import monthrange


def str2tuple(stime: str):
    """字符串时间转为元组时间"""
    return time.strptime(stime, "%Y%m%d%H")


def unix2str(ftime: float):
    """unix时间转字符串时间"""
    return time.strftime("%Y%m%d%H", time.localtime(ftime))


def str2unix(stime: str):
    """字符串时间转unix时间"""
    tupletime = str2tuple(stime)
    ret = int(time.mktime(tupletime))
    return ret


halfdayago = lambda stime: unix2str(str2unix(stime) - 3600 * 12)
onedayago = lambda stime: unix2str(str2unix(stime) - 3600 * 24)
oneweekago = lambda stime: unix2str(str2unix(stime) - 3600 * 24 * 7)


def time_str_list(t_start: str, t_end: str, interval=12):
    """
    根据起止时间,间隔生成字符串时间的列表
    :param t_start: 开始时间
    :param t_end: 结束时间
    :param interval: 间隔（小时），默认为12。
    :return: 包含两端，每隔 interval 个小时的时间列表。
    >>> time_str_list('2020040611',"2020040723")
    ['2020040611', '2020040623', '2020040711', '2020040723']
    """
    # 字符串时间转unix时间
    u_start, u_end = str2unix(t_start), str2unix(t_end)
    # 生成时间列表
    time_list = range(u_start, u_end + 1, interval * 3600)
    # 转换回字符串格式
    ret = list(map(unix2str, time_list))
    return ret


def smart_choice_time(time_=None):
    """
    给出当前时间点上最后生成文件的时间
    :return:最后生成文件的时间
    """
    # stime_now = unix2str(time.time())
    # date_now = stime_now[:-2]
    # hour_now = int(stime_now[-2:])
    #
    # ret = date_now + "11"
    # if hour_now < 3:
    #     ret = onedayago(ret)
    # elif hour_now < 15:
    #     ret = halfdayago(ret)
    # return ret
    if time_ is None:
        # 当前时间
        u_now = time.time()
    else:
        u_now = str2unix(time_)
    # 前推 4 小时，任何4小时前没有开始的数据都应该没出来
    process_time = 3600 * 4
    # 偏置 3 小时 测试结果别问我为啥
    phase = 3600 * 3
    #  周期 12 小时
    cycle = 3600 * 12
    allowed = u_now - process_time - phase
    # 去掉尾数
    u_format = allowed // cycle * cycle
    u_ret = u_format + phase
    # 转字符格式输出
    ret = unix2str(u_ret)
    return ret


def smart_choice_startend(month=time.localtime()[2]):
    """
    自动给出合适的起止时间，仅适合月榜。

    :return: t_start,t_end,m_end
    """
    year_s = str(time.localtime()[0] - (1 if month == 1 else 0))
    month_s = ("0" if month < 10 else "") + str((month - 1) % 12 + 1)

    t_start = halfdayago(year_s + month_s + "0111")
    t_end = smart_choice_time()
    m_end = year_s + month_s + str(monthrange(int(year_s), month)[1]) + "23"
    if int(m_end) > int(t_end):
        m_end = t_end
    return t_start, t_end, m_end


if __name__ == "__main__":
    print(smart_choice_time("2020071612"))
