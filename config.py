# -*- coding: utf-8 -*-
# 系统运行的配置(不需要在程序运行中修改的配置在此处定义)

# caffe主目录
caffe_root = './caffe'
# 配置文件
iniFile = './od.ini'
# 系统参数列表(用于运行系统前检查,应包含所有在iniFile文件中定义的配置项)
runningParams = [
                'mainwindowtitle',  # 系统标题
                'detectionmode',    # 检测模式
                'detectionwindowsize', # 检测窗口大小
                'nms',                 # nms
                'inputrootimagepath',  # 检测输入路径 
                'outputrootresult',    # 检测结果路径
                'loadresultpath'       # 加载检测结果路径
                ]
# 检测窗口范围
detWinMin = 1
detWinMax = 5000
# NMS范围
nmsMin = 0.3
nmsMax = 0.5