# encoding =utf-8
from cmath import tanh

from scipy.interpolate import interp1d



# from itertools import repeat


def flatter(num, edge1, edge2):
    mean = (edge1 + edge2) // 2
    expand = 2  # 多大程度上允许超越原区间
    # num 偏离区间的单位，标准化之后的结果
    sigma = expand * (edge1 - edge2) // 2
    if sigma == 0:
        # 区间长度零，插值结果多少都无所谓了
        return mean
    num_std = (num - mean) / sigma
    ret_std = tanh(num_std).real
    ret = int(ret_std * sigma + mean)
    return ret


def row_interpolate(row, fan_mode):
    """
    单行插值。最后两行的结果会再重复
    :param row:
    :param fan_mode:
    :return:
    """
    # 去除第一个行号和最后一个月度值
    data = [int(_) if _ != "" else 0 for _ in row[1:-1]]

    x_cood = range(len(data))
    interpoltor = interp1d(x_cood, data, kind="cubic")
    # 目标横坐标
    target_list = [_ / 5 for _ in range(len(data) * 5 - 5)]
    pre_ret = [flatter(int(interpoltor(x)), data[int(x)], data[int(x) + 1]) for x in target_list]
    ret_body = pre_ret + [data[-1]] * 5 + [row[-1]] * 10

    # 掉粉去除正数
    if fan_mode == "lost":
        ret_body = [0 if _ > 0 else _ for _ in ret_body]
    ret = [row[0]] + ret_body
    return ret


def table_interpolate(data, fan_mode):
    """二维表插值"""
    head = data[0]
    body = data[1:]
    ret_head = [head[0]] + [_ for data in head[1:] for _ in [data] * 5] + [head[-1]] * 5
    ret_body = [row_interpolate(_, fan_mode) for _ in body]
    ret = [ret_head] + ret_body
    return ret


if __name__ == "__main__":
    line = [517717593, 119744,
            140217, 35482, 19197, 10604, 8414, 3979, 3582, 2624, 1309, 1444, 1824, 2293, 2186, 1421, 1099, 667, 612,
            558, 574, 1045, 1428, 1423, 1111, 787, 783, 767, 646, 381, 348, 316, 305, 281, 323, 347, 291, 259, 256, 239,
            291, 183725.5]
    ret = row_interpolate(line, fan_mode="gain")
    print(ret)
    pass
