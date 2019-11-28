# -*- coding: utf-8 -*-
import configparser
import json
import numpy as np
import cv2

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
        id:一张图像中每个标注的唯一标识
        classID: 训练的结果初始值(类别序号)
        className:转化后的描述名称
        shape格式：[xmin, ymin, xmax, ymax]
        score:类别得分
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

class ImageAdjust(object):
    '''
        图像调整类
    '''

    def map(self,x, in_min, in_max, out_min, out_max):
        # 数值scale:将值从其取值范围[in_min, in_max]映射到范围[out_min, out_max]中
        return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

    def apply_brightness_contrast(self,input_img,brightness = 255, contrast = 127):
        # 图像的亮度调整
        # 界面亮度范围:-255 to 255
        # 对比度范围：-127 to 127        
        brightness = self.map(brightness, 0, 510, -255, 255)
        contrast = self.map(contrast, 0, 254, -127, 127)

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow

            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()

        if contrast != 0:
            f = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127*(1-f)

            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

        # cv2.putText(buf,'B:{},C:{}'.format(brightness,contrast),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return buf

class DetectionNet(object):
    '''
        目标检测类
        功能：完成目标检测，返回结果(运行时间，目标类别，目标位置等)
    '''

    def detect(self, image_file):
        '''
            目标检测主方法
        '''
        results_nms = np.array(
                        [
                            [5800.57080078125,  3841.69970703125, 5826.12841796875, 3901.46533203125, 0.9772407412528992, 6.0],
                            [2861.218017578125, 3324.015869140625,2944.4677734375,  3410.416015625,   0.9607754349708557, 5.0],
                            [1387.7843017578125,4094.254638671875,1455.793212890625,4191.17138671875, 0.9570822715759277, 5.0],
                            [1311.7086181640625,4144.26904296875, 1392.131103515625,4241.853515625,   0.9402307271957397, 5.0],
                            [285.3861083984375, 3626.0205078125,  396.8594665527344,3717.50390625,    0.9374492168426514, 7.0],
                            [312.70782470703125,3507.90283203125, 429.1116943359375,3583.0703125,     0.9128568172454834, 7.0],
                            [3046.605712890625, 3531.865234375,   3138.76953125,    3594.729736328125,0.9040970206260681, 2.0],
                            [275.54632568359375,3774.5009765625,  370.197998046875, 3847.8603515625,  0.7602863311767578, 7.0],
                            [4503.8466796875,   3136.585205078125,4579.6650390625,  3222.2939453125,  0.726398229598999,  5.0],
                            [2548.654541015625, 1910.8507080078125,2627.752197265625,1981.1754150390625,0.7164860963821411,26.0],
                            [230.6212921142578, 3952.7353515625,337.01934814453125, 4043.0556640625,  0.7133166790008545, 6.0],
                            [634.2503051757812, 2139.2998046875,  710.6266479492188,2203.322509765625,0.6894325017929077, 2.0],
                            [2535.7470703125,   1785.835693359375,2606.0029296875,  1868.8804931640625,0.6333261132240295,5.0]
                        ]
                    )
        time_cost = 0.3
        return [results_nms, time_cost]
        