import time
import csv
import os
import re
import sys
import subprocess

# import ppp

import paths

from diff import diff


def ds_belong(tim, offset = 0):
    tm = tim + offset*3600*24
    now = time.localtime(tm)
    hour = int(time.strftime("%H", now))
    if(hour>=11 and hour<=22):
        hourt = 11
    else:
        hourt = 23
    if(hour<11):
        return(time.strftime("%Y%m%d", time.localtime(tm-3600*12))+str(hourt))
    else:
        return(time.strftime("%Y%m%d", now)+str(hourt))



from os import listdir
from os.path import isfile, join

def bigest_file(tim):
    onlyfiles = [f for f in listdir(paths.fans) if (isfile(join(paths.fans, f)) and len(re.findall(r'^fans' + tim + '(.*)\.csv', f)) > 0)]
    if(len(onlyfiles)>0):
        fsize = {f:os.stat(paths.fans + f).st_size for f in onlyfiles}
        # 取体积最大的，若为零则忽略该文件
        fmax = max(fsize, key = fsize.get)
        if(fsize[fmax] < 1024): # 单位字节
            return(-1)
        else:
            return(fmax)
    else:
        return(-1)





if __name__ == "__main__":

    os.system('echo ------ >> Cal_cha.log')
    os.system('echo [%date:~0,10% %time%] Start Cal_cha.wl >> Cal_cha.log')

    # 识别出本次和一天前的数据并执行 Cal_cha
    today = ds_belong(time.time())
    yester = ds_belong(time.time(),-1)

    # today = ds_belong(time.time(),-0.5)
    # yester = ds_belong(time.time(),-1.5)
    # today = "2020070923"
    # yester = "2020070823"

    # 定时每天五点触发，若还没有 csv 文件则每 20min 再查一次
    while(bigest_file(today) == -1):
        os.system('echo [%date:~0,10% %time%] bigest_file(today) not yet >> Cal_cha.log')
        time.sleep(1200)

    os.system(f'echo bigest_file: {bigest_file(today)} {bigest_file(yester)} >> Cal_cha.log')

    # try:
    #     diff(today, today, paths.serv)
    #     os.system(f'echo [%date:~0,10% %time%] python diff({today}) finished >> Cal_cha.log')
    # except Exception as e:
    #     os.system(f'echo [%date:~0,10% %time%] python diff({today}) error: {e} >> Cal_cha.log')


    os.system(f'wolframscript -file {paths.serv}Cal_cha.wl {bigest_file(today)} {bigest_file(yester)} >> Cal_cha.log')

    res = str(subprocess.check_output('tail -3 Cal_cha.log', shell=True).strip())
    print("res=",res)

    if (len(re.findall(r'error',res)) > 0 or len(re.findall(r'::',res)) > 0 or len(re.findall(r'quitting',res)) > 0):
        os.system('echo [%date:~0,10% %time%] ErrorEnd Cal_cha.wl >> Cal_cha.log')
        sys.exit(1)
    else:
        os.system('echo [%date:~0,10% %time%] Fin Cal_cha.wl >> Cal_cha.log')




