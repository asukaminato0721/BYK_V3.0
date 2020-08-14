# encoding =utf-8
"""
完成本项目的配置文件控制，与
输出动画文件的congfig.csv
共计90行。
"""
import os

import paths
from library.file import fast_import, fast_export
from library.time_process import smart_choice_time, oneweekago, smart_choice_startend


class Config:
    def __init__(self, config_dir=paths.cfg):
        """

        :thisday config_dir: 文件路径，要求带斜杠
        """
        self.dir = config_dir if config_dir else ""
        if config_dir is None:
            self.config = {}
        else:
            self.config = fast_import(os.path.join(config_dir, "config.json"), "json")
        pass

    def month(self, month: int = None):
        """
        自动计算月榜或周榜的起止时间

        :thisday month:月份，0代表周榜模式。
        :return: 当前工作月份，0代表周榜模式
        """
        cfg_ = self.config
        if str(month) in "0123456789":
            cfg_['month'] = month
            if month == 0:
                cfg_['workmode'] = "week"
                cfg_['dates'] = {}
                cfg_["dates"]['t_end'] = smart_choice_time()
                cfg_["dates"]['t_start'] = oneweekago(cfg_["dates"]['t_end'])
                cfg_["dates"]['m_end'] = None
            else:
                cfg_['duration_type'] = "month"
                # cfg_["dates"] = {}
                # cfg_["dates"]['t_start'], cfg_["dates"]['t_end'], cfg_["dates"]['m_end'] = smart_choice_startend(month)
                cfg_["dates"] = dict(zip(["t_start", "t_end", "m_end"], smart_choice_startend(month)))
            cfg_['month'] = month
        return cfg_["month"]

    def gainlost(self, fan_type: str = None):
        """
        :param fan_type: 非空时设置涨掉粉
        :return: "gain"或"lost"
        """
        if fan_type:
            try:
                situation = {"gain", "lost"}
                assert fan_type in situation, "不正确的涨掉数据类型设置！"
                self.config["fan_type"] = fan_type
            except AssertionError:
                pass
            finally:
                pass
        return self.config["fan_type"]

    def t_start(self):
        return self.config["dates"]['t_start']

    def t_end(self):
        return self.config["dates"]['t_end']

    def m_end(self):
        return self.config["dates"]['m_end']

    def times(self):
        """
        注意输出是按照顺序的
        :return:
        """
        return map(self.config["dates"].get, ["t_start", "t_end", "m_end"])
        # return [self.config["dates"][_] for _ in ["t_start", "t_end", "m_end"]]

    def export(self):
        fast_export(self.config, self.dir + "config.json")


config = Config()

module_gaindata = r"data/temptate_gain.csv"
module_lostdata = r"data/temptate_lost.csv"
module_week_gaindata = r"data/temptate_week_gain.csv"
module_week_lostdata = r"data/temptate_week_lost.csv"


def generate_config(gainlost, month_: int, up_count: int = 0):
    """
    生成config文件。

    :thisday month_: 几月份，0视为周榜
    :thisday up_count: up人数。为零则是视为涨粉。
    :thisday template:模板配置文件数据
    """
    # 月份/星期数据转中文
    month_dict = {0: "一周", 1: "一月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月", 7: "七月", 8: "八月",
                  9: "九月", 10: "十月", 11: "十一月", 12: "十二月"}
    month = month_dict[month_]

    temptate = (module_gaindata if gainlost == "gain" else module_lostdata) if month_ > 0 else (
        module_week_gaindata if gainlost == "gain" else module_week_lostdata)
    cfg_ = fast_import(temptate)
    if up_count == 0:
        # 说明是涨粉
        cfg_[1] = [fr"'本文件为 {month} 涨粉榜配置文件！'"]
        cfg_[39][1] = month + "净涨粉"
    else:
        # 是掉粉，那么事情就会比较多
        cfg_[1] = [f"本文件为 {month} 掉粉榜配置文件！本周期上榜up人数共有 {up_count} 人！"]
        cfg_[39][1] = month + "净掉粉"
        # 对焦排名
        cfg_[75][0] = cfg_[75][1] = up_count
        # 窗口位置对齐
        cfg_[21][0] = str(int(1010 - 49.5 * up_count))
        cfg_[52][0] = str(int(-70 - 49.5 * up_count))
    fast_export(cfg_, "anime/config.csv")


if __name__ == "__main__":
    generate_config(7, 100)
