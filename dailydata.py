# encoding =utf-8
"""
这是最复杂的文件之一。
"""
import time
from typing import Dict, List

import paths
from cfg import Config
from library.file import replaceAll, log, stime2filename, fast_import
from library.time_process import time_str_list, str2tuple

pre = paths.serv

week_eng2chs = {"Mon": "周一", "Tue": "周二", "Wed": "周三", "Thu": "周四", "Fri": "周五",
                "Sat": "周六", "Sun": "周日", "11时": "日", "23时": "夜"}


# eng2chs_rule = lambda date: replaceAll(time.strftime("%Y年%m月%d日（%a）", str2tuple(date)), week_eng2chs)
def eng2chs_rule(date, lenstr="yyyy年mm月dd日（周x）"):
    s1 = time.strftime("%Y年%m月%d日（%a）%H时".encode('unicode_escape').decode('utf8'), str2tuple(date)).encode(
        'utf-8').decode('unicode_escape')
    s = replaceAll(s1, week_eng2chs)
    return s[:min(len(lenstr), len(s))]


def dailydata(date, ups, target="fan"):
    """
    根据给定日期的变化速率挑选出其中指定的up数据作为一行，例如：
        dailydata("2020040523",[2,5,8,12])给出2020年4月5日23点的文件中uid为2,5,8,12的数据
    :param target: 目标参数，默认为涨粉。
        有待后续开发来使得契合总榜。
    :param date: 变化速率文件（cha文件） 的日期和小时
    :param ups: 要挑选的up名单。
    :return: {ups:value},若当天没有数据，值为None。
    """
    cha_file = pre + stime2filename(date, "cha")
    cha_data = fast_import(cha_file)[1:]
    # uid0 名字1 粉丝量3 视频数4 视频播放5 关注数7 专栏阅读8 等级9 充电10 点赞11，从零开始
    ups_data = {i[0]: int(i[3]) for i in cha_data if (i[0] in ups or int(i[0]) in ups)}
    return ups_data
    # return {ups: None for ups in ups}


def daysdata(ups: list, config: Config):
    """
        统计每日数据，并且报告输出情况。还负责得到月度数据。
        @param config: 涨掉粉变量
        @param ups: 要统计的up名单列表
        @return: 每个up一行，汇总各天数据+月度数据。
        """
    # 时间处理
    t_start, t_end, m_end = config.times()
    day_list, day_names = get_time(t_start, t_end, m_end)
    # 存放的数据格式：{day_name:{up:data of the day}}
    # 月内数据
    data = {date: dailydata(date, ups) for date in day_list["month"]}
    # 统计月度数据，缺数据情况报告
    month_data = report_month_data(data, ups, day_list["month"], day_list)
    # 取得本月余下数据
    data.update({date: dailydata(date, ups) for date in day_list["rest"]})
    # 输出
    ret = get_ret(data, day_list["all"], day_names, month_data, ups, config)
    return ret


def get_time(t_start, t_end, m_end):
    if m_end is None or int(m_end) > int(t_end):
        m_end = t_end
    day_list = {"month": time_str_list(t_start, m_end), "rest": time_str_list(m_end, t_end)[1:]}
    day_list["all"] = day_list["month"] + day_list["rest"]
    day_names: list = [eng2chs_rule(dates) for dates in time_str_list(t_start, t_end)]
    return day_list, day_names


def get_ret(data, day_name_keys: list, day_names: list, month_data, ups, config):
    """

    @param config: 月份
    @param data: 总数据
    @param day_name_keys: 月份名字
    @param day_names: 月份名字正文
    @param month_data:
    @param ups:up名单

    """
    # 按照月份数据排序
    sorted_ups = sorted(ups, key=month_data.get, reverse=True)
    # 准备生成返回值
    # 表头
    ret_head = get_head(day_names, config)
    # 表体，每个up一行，相当于最后输出的一列。
    ret_body = [[up] + get_up_data(data, day_name_keys, up) + [month_data[up]] for up in
                sorted_ups]
    ret = ret_head + ret_body
    return ret


def get_up_data(data, day_name_keys, up):
    ret = [data[day_name_key].get(up, 0) for day_name_key in day_name_keys]
    return ret


def get_head(day_names, config: Config):
    # 最后总变化榜单行首内容
    month_title = f"{'月度' if config.month() else '一周'}净{'涨粉' if config.gainlost() == 'gain' else '掉粉'}"
    ret_head = [[".png"] + day_names + [month_title]]
    return ret_head


def report_month_data(data: Dict[str, dict], ups: List[int], month_day_list: List[str], day_list):
    """
    统计月度数据，报告漏数据情况

    @param day_list:
    @param ups: up名单
    @param data: 存放每日每个up的数据
    @param month_day_list:List[day_name] 月内日期
    """
    error_ups, month_data = get_month_data(data, day_list["month"], ups)
    log(f"在统计榜单时发现的无数据账号共{len(error_ups)}位，如下：")
    for errup in error_ups:
        log(f"error mid:{errup}，周期累计值：{error_ups[errup]}")
        lost_days = [day for day in month_day_list if errup not in data[day]]
        log(f"  合计{len(lost_days)}个半天:", "\t".join(date[4:] for date in lost_days))
    return month_data


def get_month_data(data, month_day_list, ups):
    # {up:month_data}
    month_data = {}
    error_ups: Dict["up":"month_data"] = {}
    for up in ups:
        month_data[up] = 0
        for date in month_day_list:
            try:
                # 实际增长是半天的，要除以二
                month_data[up] += data[date].get(up, None) // 2
            except (TypeError, KeyError):
                # 说明取到的是None，当天没有数据
                error_ups[up] = month_data[up]
    return error_ups, month_data


if __name__ == "__main__":
    pass
