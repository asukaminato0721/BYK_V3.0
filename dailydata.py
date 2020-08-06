# encoding =utf-8
"""
这是最复杂的文件之一。
"""
import time

from library.file import replaceAll, log, stime2filename, fast_import
from library.time_process import time_str_list, str2tuple

pre = r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp""\\"
if __name__ == "__main__":
    pass

week_eng2chs = {"Mon": "周一", "Tue": "周二", "Wed": "周三", "Thu": "周四", "Fri": "周五",
                "Sat": "周六", "Sun": "周日", "11时": "日", "23时": "夜"}
eng2chs_rule = lambda date: replaceAll(time.strftime("%Y年%m月%d日（%a）", str2tuple(date)), week_eng2chs)


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
    ups_data = {i[0]: int(i[3]) if i[0] in ups or int(i[0]) in ups else None for i in cha_data}
    return ups_data
    # return {ups: None for ups in ups}


def daysdata(t_start: str, t_end: str, m_end: str, ups: list, fan_mode="gain"):
    """
        统计每日数据，并且报告输出情况。还负责得到月度数据。
        :param ups: 要统计的up名单列表
        :param fan_mode: 涨粉还是掉粉
        :param t_start: 统计开始时间
        :param m_end: 月度结束时间，周榜为None
        :param t_end: 统计结束时间
        :return: 每个up一行，汇总各天数据+月度数据。
        """
    # 周榜或不足月情况
    if m_end is None or int(m_end) > int(t_end):
        m_end = t_end

    month_day_list = time_str_list(t_start, m_end)
    month_day_names = [eng2chs_rule(dates) for dates in month_day_list]
    # 存放的数据格式：{day_name:{up:data of the day}}
    # 先计算月（周）内的粉丝变化情况
    data = {date: dailydata(date, ups) for date in month_day_list}

    # 统计月度数据
    # {up:month_data}
    month_data = {}
    error_ups = set()
    for up in ups:
        month_data[up] = 0
        for date in month_day_list:
            try:
                # 实际增长是半天的，要除以二
                month_data[up] += data[date][up] // 2
            except TypeError:
                # 说明取到的是None，当天没有数据
                error_ups.add(up)

    # 缺数据情况报告
    log(f"在统计月榜时发现的无数据账号共{len(error_ups)}位，如下：")
    for errup in error_ups:
        log(f"    error mid:{errup}，月度累计值：{month_data[errup]}")
        # for day in month_day_list:
        #     if data[day][errup] is None:
        #         lost_days.append(day)
        lost_days = [day for day in month_day_list if data[day][errup] is None]
        print(f"合计{len(lost_days)}个半天,如下：\n", lost_days)

    # 取得本月余下数据
    rest_day_list = time_str_list(m_end, t_end)[1:]
    rest_day_names = [eng2chs_rule(dates) for dates in rest_day_list]
    data.update({date: dailydata(date, ups) for date in rest_day_list})

    # 输出
    # 按照月份数据排序
    sorted_ups = sorted(ups, key=lambda v: month_data[v], reverse=True)

    day_name_keys = month_day_list + rest_day_list
    day_names = month_day_names + rest_day_names

    # 准备生成返回值
    # 表头
    ret_head = [[".png"] + day_names + ["月度净" + ("涨粉" if fan_mode == "gain" else "掉粉")]]

    # 表体，每个up一行，相当于最后输出的一列。
    ret_body = [[up] + [data[day_name_key][up] for day_name_key in day_name_keys] + [month_data[up]] for up in
                sorted_ups]
    ret = ret_head + ret_body
    return ret


if __name__ == "__main__":
    pass
