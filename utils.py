# -*- coding: utf-8 -*-
import configparser
import json

class ODConfig(object):
    '''
        ini配置文件帮助类
    '''
    def __init__(self, iniFile):
        self.config = configparser.ConfigParser()
        self.config.read(iniFile, encoding='UTF-8')

    def ConfigSectionMap(self,section):
        d = {}
        options = self.config.options(section)
        for option in options:
            try:
                d[option] = self.config.get(section, option)
                if d[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                # print("exception on %s!" % option)
                d[option] = None
        return d 

    def reloadIniFile(self,iniFile):
        self.config.read(iniFile, encoding='UTF-8')


class DetectResult(object):
    '''
        检测结果帮助类
        标注Json文件格式：
        {
            "imgFile": "./test.jpg",
            "shapes":
            [
                {
                    "id" : 1,
                    "classID" : 34,
                    "className": "t1,v2.s3", 
                    "shape" : [1200,1800,1500,2100]
                },
                {
                    "id": 2,
                    "classID" : 25,
                    "className": "t3,v2.s0", 
                    "shape" : [500,2000,600,2200]
                },
                {
                    "id": 3,
                    "classID" : 18,
                    "className": "t6,v1.s0", 
                    "shape" : [1830,1740,1910,1840]
                }
            ]
            }
        id:一张图像中每个标注的唯一标识
        classID: 训练的结果初始值(类别序号)
        className:转化后的描述名称
        shape格式：[xmin, ymin, xmax, ymax]
    '''
    def __init__(self,annoJsonFile=None):
        self.annoJsonFile = annoJsonFile

    def getImageFileName(self):
        '''
            图像名称
            返回：str
        '''
        if not self.annoJsonFile is None:
            with open(self.annoJsonFile, 'r') as f:
                jdata = json.load(f)
                imgFile = jdata['imgFile']
                return imgFile

        return None

    def getImageAnnos(self):
        '''
            标注
            返回：列表
        '''
        if not self.annoJsonFile is None:
            with open(self.annoJsonFile, 'r') as f:
                jdata = json.load(f)
                annos = jdata['shapes']
                return annos
                
        return None