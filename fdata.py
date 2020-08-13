# encoding =utf-8
import csv
import json
import time

import pymysql
import requests

from library.file import log

import paths
url_template = "https://api.bilibili.com/x/article/archives?ids="
# TODO 若没有此文件夹则新建文件夹
out_file = paths.byk + "anime\\fdata.csv"
# out_file = "fdata.csv"


# 目标观看量：10万
def export_fdata(ups_, target_month_, target_view_=100000):
    """
    从服务器获取数据并且输出到目标目录。
    :param target_view_: 目标观看数
    :param target_month_: 目标月份
    :param ups_:up名单
    :return:
    """
    log(f"up信息读取完毕，共{len(ups_)}个，开始获取稿件...")

    # sql操作
    mid_list = ','.join([str(_) for _ in ups_])
    month_list = ','.join([str(_) for _ in target_month_])
    sql = "SELECT aid, pubdate, mid, title FROM video_static WHERE" \
          f" mid in ({mid_list}) and DATE_FORMAT(pubdate , '%Y%m') IN ({month_list})"
    db = pymysql.connect(host="cdb-ilksgvwk.bj.tencentcdb.com", port=10202, user="leptc", passwd="leptc_up",
                         db="bilibili", use_unicode=True, charset="utf8mb4")
    cursor = db.cursor()
    # 服务器执行，这一步会比较慢，大约30s
    log("正在沟通远端服务器，过程较长（2-3min），请耐心等待。")
    t0 = time.time()
    cursor.execute(sql)
    dat = cursor.fetchall()
    log(f"远端数据获取成功，正在处理。本次耗时{time.time() - t0}秒。")
    video_list = [info[0] for info in dat]
    total_len = len(video_list)
    log(f'{target_month_}稿件获取完毕，共{total_len}个，开始获取播放量')

    view_dict = {}
    for ids in range(total_len // 100 + 1):
        try:
            url = url_template + ','.join([str(i) for i in video_list[ids * 100: min(ids * 100 + 100, total_len)]])
            page = requests.get(url).text
            results = json.loads(page)['data']
            view_dict.update({int(aid): info['stat']['view'] for (aid, info) in results.items()})
            log(f"获取进度：{len(view_dict)}/{total_len}", end='\r')
        except Exception as e:
            log('\n', ids, e)

    log(f'\n播放量获取完毕，共{len(view_dict)}个有效视频，开始输出')

    with open(out_file, "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['pubdate', 'mid', 'title', 'view', 'aid'])
        for (aid, pubdate, mid, title) in dat:
            if view_dict.get(aid, -1) > target_view_:
                writer.writerow(
                    [pubdate.strftime("%Y年%m月%d日"), mid, title.replace(',', '，'),
                     view_dict.get(aid, -1), aid])
    log(f'数据已保存至\t{out_file}')


if __name__ == '__main__':
    from library.file import fast_import

    ups = fast_import(r"D:\OneDrive\LiWorkshop\BiliYuekan_Remake\temp\ups.csv")[0]
    export_fdata(ups, ["202007", "202008"])
