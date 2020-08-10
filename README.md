# README

## 可能需要调整的参数
工作目录：main文件中的default_absolute_dir等变量
配置文件路径：main文件中的config_dir变量
差文件的存放路径：main文件中的cha_dir变量,dailydata文件中的pre变量
fdata输出文件路径：fdata文件中的out_file变量
日志输出方式：library文件夹下file文件中的log函数
涨掉粉数据模板：enconfig文件下module_lostdata和module_gaindata等参数
（不知道周榜模板要怎么弄）

## 输入参数
本次工作流程是涨粉还是掉粉，键盘输入gain或者lost
本次工作流程是周榜还是月榜，键盘输入0或者对应月份
是否需要做差，键盘输入0或者1
（服务器上跑应该是不要的，但是不知道到时候怎么部署所以先保留，
要改的话调整main文件21-25行内容即可，对应代码如下，注释即可）
```
# diff(elective,get cha files)
need_diff = input("是否做差？0=已有/1=要")
if need_diff == "1":
    cha_dir = default_absolute_dir + "temp"
    diff(config.t_start(), config.t_end(), cha_dir)
```

## 目录描述


### code
存放py文件。

### amine
动画输出。
- 头像
- fdata.csv
- data.csv
- config.csv
- flash，swf模板
- 背景图

### temp
依赖的各种文件；
fan cha cha_server etc
中间文件。
up名单
原始数据列表
插值数据列表

## 变量命名规范
- t_start：一次数据处理开始的时间。
- m_end：一次数据处理中月份结束的时间。
- t_end：一次数据处理结束的时间

        仅对月榜有效。一般为当月最后一天23时；
        如果比t_end晚应当被重设为与t_end相同。
- fan_mode：取值为gain和lost，标记是涨粉还是掉粉。



## 日志

- 20200810
    - 狸子首次 merge 到氘化氢
    - 💡：标准化路径 `import paths`
    - 💡：狸工智能日报的 `Cal_cha.py` 合并到此项目，因为要用到 `diff`












