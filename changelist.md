# Changelist

## FIX
不再可能导致出现做差导致的数据异常bug。

## IMPROVE
fast_import() 和 fast_export 现在可以输入输出 json 文件。
stime2filename()增加注释。
生成的配置文件增加对于周榜的兼容程度。

## CHANGE
修复了全局变量的一个拼写错误。

将原来的libs中的函数分散到 file和time两个文件中。
- halfdayago(),onedayago(),oneweekago() 现在从函数实现改为 lambda 表达式实现。
- list2dictuple() 函数的实现现在移入subb（现diff）文件
- 调整了 smart_choice_time() 的输出时间阈值，来配合新的更快的爬虫。
- str2filename 改名为stime2filename()，现在兼容给出多种后缀的fan文件。

myimport 和config 合并，重命名为 config。
- 重写了其中大部分函数。
- fantype()更名为gainlost()

subb模块改为diff模块。
- fandata()改名为fan_dict_data()，现在直接给出字典化的数据。
- 修改了cha()函数不再执行字典化的过程。
- 为了提高数据安全性，效率大约下降了25%。

myselect模块改名为get_ups
- givetop() 改名为 select_from_a_file()，现在不再兼容旧版做差数据

daily_data_模块
- days_data()不再兼容旧版差文件

## REMOVE
删除了 log 和 warn 函数。
stime2filename 函数不再支持寻找 cha_month 文件。
现在计算月榜名单是自动的，不用再重新寻找月度榜首。