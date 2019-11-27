import sys
import os
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

from mainWindow import *
from configureWindow import *
from brightnessAndContrastAdjustWindow import *
import config
from utils import ODConfig, DetectResult, DetectionNet
import configparser
import cv2
import numpy as np
from pathlib import Path
import json

# 批量检测发送信号消息
MSG_PAUSE = 'pause'
MSG_RESUME = 'resume'
MSG_STOP = 'stop'
MSG_FINISHED = 'finished'
# 配置窗口发送信号
MSG_CONF_COMPLETED = 'completed'

class singleDetection(object):
    '''
        单张检测类
    '''
    def __init__(self, inputRootImagePath=None, resultOutputPath=None):
        # 单张检测图像根目录
        self.inputRootImagePath = inputRootImagePath    
        self.resultOutputPath = resultOutputPath 

        # 获得输入目录的底层路径名
        inputPath = Path(self.inputRootImagePath)
        inputPath_parent = inputPath.parent
        self.lastPathOfInputPath = inputPath.relative_to(inputPath_parent)

    def detect(self, imgFileName):
        filePath, fileName = os.path.split(imgFileName)
        fileNameWithFullPath = Path(imgFileName).as_posix()
        [all_results, const_time] = DN.detect(fileNameWithFullPath)
        # 构造json文件内容
        data = {}
        data['imgFile'] = fileNameWithFullPath
        data['shapes'] = []
        shapeCount = all_results.shape[0]
        for i in range(shapeCount):
            shape = {}
            shape['id'] = i + 1
            shape['classID'] = int(all_results[i][5])
            shape['className'] = str(all_results[i][5])
            shape['shape'] = [
                                int(all_results[i][0]),
                                int(all_results[i][1]),
                                int(all_results[i][2]),
                                int(all_results[i][3]),
                            ]
            shape['score'] = all_results[i][4]

            data['shapes'].append(shape)                    

        #检测结果(json文件)存放目录 
        structure = Path(self.resultOutputPath).joinpath(self.lastPathOfInputPath).joinpath(Path(filePath).as_posix()[len(Path(self.inputRootImagePath).as_posix())+1:])
        # print(imgFileName)
        # print(structure)
        
        # 创建目录
        structure.mkdir(parents=True, exist_ok=True)
        # 检测结果json文件
        fName,ext = os.path.splitext(fileName)
        jsonFileName = structure.joinpath(fName + '.json')
        # 写入文件
        with open(jsonFileName.as_posix(), 'w') as f:
            json.dump(data, f)

        return jsonFileName.as_posix()
        

class batchDetectionThread(QtCore.QThread):
    '''
        批量检测子进程
    '''
    # 进度信号(处理张数，处理图像文件名[全路径]，检测结果json文件名[全路径])
    change_progress = QtCore.pyqtSignal(int,str,str)

    def __init__(self, parent=None, inputRootImagePath=None, resultOutputPath=None):
        QtCore.QThread.__init__(self, parent)
        # 批量检测图像根目录
        self.inputRootImagePath = inputRootImagePath    
        self.resultOutputPath = resultOutputPath 

        # 获得输入目录的底层路径名
        inputPath = Path(self.inputRootImagePath)
        inputPath_parent = inputPath.parent
        self.lastPathOfInputPath = inputPath.relative_to(inputPath_parent)

        # 暂停、恢复
        self.sync = QtCore.QMutex()
        self.pauseCond = QtCore.QWaitCondition()
        self.stopCond = QtCore.QWaitCondition()
        self.isPause = False  
        self.isStop = False

        
        # 与主进程的通信
        w.batchDetectionSignal.connect(self.detectionSignal)

    def detectionSignal(self,s):
        print('receiving signal:{}'.format(s))
        if s == MSG_PAUSE:            
            self.pause()
        elif s == MSG_RESUME:            
            self.resume()
        elif s == MSG_STOP:
            self.stop()

    def resume(self):
        self.sync.lock()
        self.isPause = False
        self.isStop = False
        self.sync.unlock()
        self.pauseCond.wakeAll()

    def pause(self):
        self.sync.lock()
        self.isPause = True
        self.isStop = False
        self.sync.unlock()        

    def stop(self):
        print('in stop func in thread')
        self.sync.lock()
        self.isPause = False
        self.isStop = True
        self.sync.unlock() 

    def run(self): 
        for i in range(len(w.allImageFiles)):
            self.sync.lock()
            if self.isStop:
                print('stopped')
                self.stopCond.wait(self.sync)
                break
            self.sync.unlock()

            self.sync.lock()          
            if self.isPause:
                print('pausing ...')
                self.pauseCond.wait(self.sync)
            self.sync.unlock()

            w.currentImgIndex = i

            imgFileName = w.allImageFiles[i]
            filePath, fileName = os.path.split(imgFileName)
            fileNameWithFullPath = Path(imgFileName).as_posix()
            [all_results, const_time] = DN.detect(fileNameWithFullPath)
            # 构造json文件内容
            data = {}
            data['imgFile'] = fileNameWithFullPath
            data['shapes'] = []
            shapeCount = all_results.shape[0]
            for i in range(shapeCount):
                shape = {}
                shape['id'] = i + 1
                shape['classID'] = int(all_results[i][5])
                shape['className'] = str(all_results[i][5])
                shape['shape'] = [
                                    int(all_results[i][0]),
                                    int(all_results[i][1]),
                                    int(all_results[i][2]),
                                    int(all_results[i][3]),
                                ]
                shape['score'] = all_results[i][4]

                data['shapes'].append(shape)                    

            #检测结果(json文件)存放目录 
            structure = Path(self.resultOutputPath).joinpath(self.lastPathOfInputPath).joinpath(Path(filePath).as_posix()[len(Path(self.inputRootImagePath).as_posix())+1:])
            # print(imgFileName)
            # print(structure)
            
            # 创建目录
            structure.mkdir(parents=True, exist_ok=True)
            # 检测结果json文件
            fName,ext = os.path.splitext(fileName)
            jsonFileName = structure.joinpath(fName + '.json')
            # 写入文件
            with open(jsonFileName.as_posix(), 'w') as f:
                json.dump(data, f)

            self.change_progress.emit(1, fileNameWithFullPath, jsonFileName.as_posix()) 
        '''
            下面的方式也可以实现批量检测，不能监测当前进度
        '''
        # # 获得输入目录的底层路径名
        # inputPath = Path(self.inputRootImagePath)
        # inputPath_parent = inputPath.parent
        # lastPathOfInputPath = inputPath.relative_to(inputPath_parent)
        # for root, dirs, files in os.walk(self.inputRootImagePath):
        #     for fileName in files:
        #         self.sync.lock()
        #         if self.isStop:
        #             print('stopped')
        #             self.stopCond.wait(self.sync)
        #             break
        #         self.sync.unlock()

        #         self.sync.lock()          
        #         if self.isPause:
        #             print('pausing ...')
        #             self.pauseCond.wait(self.sync)
        #         self.sync.unlock()

        #         if fileName[fileName.rfind('.'):].upper() == '.JPG':  
        #             fileNameWithFullPath = Path(root).joinpath(fileName).as_posix()                                     
        #             print(fileNameWithFullPath)
        #             # 进行检测,获得结果
        #             [all_results, const_time] = DN.detect(fileNameWithFullPath)
        #             # 构造json文件内容
        #             data = {}
        #             data['imgFile'] = fileNameWithFullPath
        #             data['shapes'] = []
        #             shapeCount = all_results.shape[0]
        #             for i in range(shapeCount):
        #                 shape = {}
        #                 shape['id'] = i + 1
        #                 shape['classID'] = int(all_results[i][5])
        #                 shape['className'] = str(all_results[i][5])
        #                 shape['shape'] = [
        #                                     int(all_results[i][0]),
        #                                     int(all_results[i][1]),
        #                                     int(all_results[i][2]),
        #                                     int(all_results[i][3]),
        #                                 ]
        #                 shape['score'] = all_results[i][4]

        #                 data['shapes'].append(shape)                    

        #             fName,ext = os.path.splitext(fileName)  
        #             #检测结果(json文件)存放目录 
        #             structure = Path(self.resultOutputPath).joinpath(lastPathOfInputPath).joinpath(Path(root).as_posix()[len(Path(inputPath).as_posix())+1:])
        #             # 创建目录
        #             structure.mkdir(parents=True, exist_ok=True)
        #             # 检测结果json文件
        #             jsonFileName = structure.joinpath(fName + '.json')
        #             # 写入文件
        #             with open(jsonFileName.as_posix(), 'w') as f:
        #                 json.dump(data, f)
                                  
        #             # time.sleep(0.1)
        #             # fileNameWithFullPath = os.path.join(root, fileName)
                    
        #             # 处理完一张，发送消息更新进度条和界面
        #             self.change_progress.emit(1, fileNameWithFullPath, jsonFileName.as_posix())  
        #     else:
        #         continue
        #     break      

        #完成批量检测
        self.change_progress.emit(0, MSG_FINISHED, '')     


class BrightnessAndContrastAdjustWindow(QDialog):
    '''
        亮度和对比度调整窗口
    '''
    # 图像调整发送信号,由主窗口处理
    brightness_contrast_params_signal = QtCore.pyqtSignal(float, int)
    def __init__(self):
        super().__init__()

        self.ui = Ui_DialogBrightnessAndContrastAdjust()
        self.ui.setupUi(self)

        self.initWindow()

    def initWindow(self):
        # 模态窗口
        self.setWindowModality(QtCore.Qt.WindowModal)

        # 事件
        self.ui.pushButtonReset.clicked.connect(self.reset)
        self.ui.pushButtonOK.clicked.connect(self.ok)

    def reset(self):
        self.ui.spinBoxBrightness.setValue(0)
        self.ui.spinBoxContrast.setValue(0)
        self.brightness_contrast_params_signal.emit(0.0, 0)

    def ok(self):
        # 调整参数  alpha:[1.0,3.0]  beta:[0-100]        
        alpha =  1.0 + self.ui.spinBoxContrast.value() / 100
        beta = self.ui.spinBoxBrightness.value()

        self.brightness_contrast_params_signal.emit(alpha, beta)         
     
       


class ConfigureWindow(QDialog):
    '''
        配置参数窗口
    '''
    # 配置完成信号
    config_signal = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.ui = Ui_DialogConfig()
        self.ui.setupUi(self)

        self.conf = ODConfig(config.iniFile)

        self.initWindow()

    def initWindow(self):
        detecMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detecMode == 2: #加载检测结果模式
            self.displayDetectResultUI()
        else:
            self.displayDetectUI()
        

        # 检测参数文本框
        reg_ex = QtCore.QRegExp("[0-9]{1,4}")
        input_validator = QRegExpValidator(reg_ex, self.ui.lineEditDetectWindowSize)
        self.ui.lineEditDetectWindowSize.setValidator(input_validator)
        reg_ex = QtCore.QRegExp("[0][.][3-5]")
        input_validator = QRegExpValidator(reg_ex, self.ui.lineEditNMS)
        self.ui.lineEditNMS.setValidator(input_validator)

        # 路径选择文本框
        self.ui.lineEditInputPath.setReadOnly(True)
        self.ui.lineEditOutPutPath.setReadOnly(True)
        # 检测结果路径选择文本框
        self.ui.lineEditDetectResult.setReadOnly(True)
        # 模态窗口
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # 按钮事件
        self.ui.radioButtonSingleDetectMode.clicked.connect(self.radioButtonModeSelect)
        self.ui.radioButtonBatchDetectMode.clicked.connect(self.radioButtonModeSelect)
        self.ui.radioButtonLoadDetectResult.clicked.connect(self.radioButtonModeSelect)
        

        self.ui.pushButtonOk.clicked.connect(self.clickOK)
        self.ui.pushButtonCancel.clicked.connect(self.clickCancel)

        self.ui.pushButtonPathSelect4Input.clicked.connect(self.selInputPath)
        self.ui.pushButtonPathSelect4Output.clicked.connect(self.selOutputPath)

        self.ui.pushButtonPathSelect4DetectResult.clicked.connect(self.selResultPath)
       
    def displayDetectResultUI(self):        
        self.ui.groupBoxDetectParams.setVisible(False)
        self.ui.groupBoxPathSelect.setVisible(False)
        self.ui.groupBoxDetectResult.setVisible(True)

    def displayDetectUI(self):
        self.ui.groupBoxDetectParams.setVisible(True)
        self.ui.groupBoxPathSelect.setVisible(True)
        self.ui.groupBoxDetectResult.setVisible(False)

    def radioButtonModeSelect(self):
        if self.ui.radioButtonLoadDetectResult.isChecked():
            self.displayDetectResultUI()
        else:
            self.displayDetectUI()
        

    def clickOK(self):
        '''
            保留当前设置，退出
        '''        
        # 检测模式(0:逐张检测， 1：批量将测， 2：加载检测结果)
        if self.ui.radioButtonSingleDetectMode.isChecked():
            detecMode = 0
        elif self.ui.radioButtonBatchDetectMode.isChecked():
            detecMode = 1
        else:
            detecMode = 2

        # 检测参数
        detectWindowSize = self.ui.lineEditDetectWindowSize.text()
        if len(detectWindowSize.strip()) == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("检测窗口参数不能为空!")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('确定', QMessageBox.YesRole)         
            
            msgBox.exec()  
            self.ui.lineEditDetectWindowSize.setFocus(True)
            return      

        if (int(detectWindowSize) < config.detWinMin) or \
            (int(detectWindowSize) > config.detWinMax) :
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("检测窗口参数不在范围内，请重新设置!")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('确定', QMessageBox.YesRole)         
            
            msgBox.exec()  
            self.ui.lineEditDetectWindowSize.setFocus(True)
            return  

        nms = self.ui.lineEditNMS.text()
        if len(nms.strip()) == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("NMS参数不能为空!")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('确定', QMessageBox.YesRole)         
            
            msgBox.exec()   
            return     
        # 路径设置   
        inputPath = self.ui.lineEditInputPath.text()
        if len(inputPath.strip()) == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("输入路径参数不能为空!")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('确定', QMessageBox.YesRole)         
            
            msgBox.exec()   
            return  
        
        outputPath = self.ui.lineEditOutPutPath.text()
        if len(outputPath.strip()) == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("输出路径参数不能为空!")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('确定', QMessageBox.YesRole)         
            
            msgBox.exec()   
            return 
        loadresultpath = self.ui.lineEditDetectResult.text()
        if len(loadresultpath.strip()) == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("检测结果路径参数不能为空!")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('确定', QMessageBox.YesRole)         
            
            msgBox.exec()   
            return 
        # 写入参数        
        self.conf.config.set('App','detectionmode',str(detecMode))
        self.conf.config.set('App','detectionwindowsize',str(int(detectWindowSize)))
        self.conf.config.set('App','nms',nms)
        self.conf.config.set('App','inputrootimagepath',inputPath)
        self.conf.config.set('App','outputrootresult',outputPath)
        self.conf.config.set('App','loadresultpath',loadresultpath)
        with open(config.iniFile,'w', encoding="utf-8") as f:
            self.conf.config.write(f)
        
        # 完成配置发送信号
        self.config_signal.emit(MSG_CONF_COMPLETED)
        self.accept()

    def clickCancel(self):
        '''
            取消当前设置，退出
        '''
        self.reject()
        

    def selInputPath(self):
        file = str(QFileDialog.getExistingDirectory(self, "选择待检测图像目录"))
        if len(file) > 0 :
            self.ui.lineEditInputPath.setText(file)
     
    def selOutputPath(self):
        file = str(QFileDialog.getExistingDirectory(self, "选择检测结果存放目录"))
        if len(file) > 0 :
            self.ui.lineEditOutPutPath.setText(file)

    def selResultPath(self):
        file = str(QFileDialog.getExistingDirectory(self, "选择检测结果存放目录"))
        if len(file) > 0 :
            self.ui.lineEditDetectResult.setText(file)


class ObjectDetectionMainWindow(QMainWindow):  
    
    batchDetectionSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        

        # 将进度条加入状态栏 
        self.progressBar = QProgressBar()          
        self.ui.statusbar.addPermanentWidget(self.progressBar,0)  
        

        # 图像调整窗口
        self.brightnessAndContrastAdjustWindow = None
        # 当前图像的QImage(用于还原调整)
        self.oriQImage = None

        # 批量检测标志(True标识已经开始批量检测，开始按钮不是第一次点击)
        self.batchStart = False
        # 是否批量检测中
        self.batchDetInRunning = False 

        # 逐张检测和批量检测存放的所有图像列表
        self.allImageFiles = []
        # 加载结果
        self.allAnnoFiles = []
        # 当前检测或加载的图像索引
        self.currentImgIndex = 0

        # 配置文件
        self.conf = ODConfig(config.iniFile)
                

        self.setUI()

    def setUI(self):
        # 主窗口标题
        self.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
        # 左侧显示工具栏
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.ui.toolBar)    
        # 工具栏按钮初始状态
        self.ui.actionStart.setEnabled(False)
        self.ui.actionPause.setEnabled(False)
        self.ui.actionStop.setEnabled(False)
        self.ui.actionNext.setEnabled(False)
        self.ui.actionPrev.setEnabled(False)
        self.ui.actionRedo.setEnabled(False)
        self.ui.actionImageAdjust.setEnabled(False)
        # 隐藏日志窗口        
        self.ui.dockWidgetLog.setMinimumSize(400,200)
        self.ui.dockWidgetLog.setVisible(False)
        # 状态栏
        self.ui.statusbar.showMessage('准备就绪。')  

        # 设置ListWidget显示模式
        self.ui.listWidgetCropImages.setViewMode(QListView.IconMode)
        # 设置ListWidget显示图像大小
        # self.ui.listWidgetCropImages.setIconSize(QtCore.QSize(150,100))
        # 设置ListWidget禁止拖放
        self.ui.listWidgetCropImages.setMovement(QListView.Static)        

        # Actions
        self.ui.actionSetup.triggered.connect(self.configure)
        self.ui.actionDisplayLog.triggered.connect(self.showOrHideLog)
        self.ui.actionStart.triggered.connect(self.startDetection)
        self.ui.actionPause.triggered.connect(self.pauseDetection)
        self.ui.actionStop.triggered.connect(self.stopDetection)
        self.ui.actionNext.triggered.connect(self.nextImage)  
        self.ui.actionPrev.triggered.connect(self.prevImage)
        self.ui.actionImageAdjust.triggered.connect(self.brightnessAndContrastAdjust)
        # 调用系统的close事件(执行的是closeEvent)
        self.ui.actionExit.triggered.connect(self.close)
        # 裁剪小图的事件
        self.ui.listWidgetCropImages.itemClicked.connect(self.onListWidgetItemClicked)
        # 自定义信号:处理从imageview中选择一个标注时的事件
        self.ui.imageView.annoRectSelected.connect(self.onSelectOneAnnoRect)

    def onListWidgetItemClicked(self,item):
        # print(item.data(Qt.UserRole))
        itemId = item.data(QtCore.Qt.UserRole)
        self.ui.imageView.selectAnnoRectById(itemId)

    def onSelectOneAnnoRect(self,id):
        # 接收所选的标注id，在crop列表中选择它
        # print('selected id is {}'.format(id))
        for i in range(self.ui.listWidgetCropImages.count()):
            item = self.ui.listWidgetCropImages.item(i)
            itemId = item.data(QtCore.Qt.UserRole)
            if itemId == id:
                item.setSelected(True)

    def closeEvent(self, event):
        # 重写主窗口的close事件，加入关闭逻辑
        if self.batchDetInRunning:  #批量检测进程运行中
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("正在检测中，退出将终止现有检测，是否继续退出？")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('是', QMessageBox.YesRole)            
            msgBox.addButton('否',QMessageBox.NoRole)          
            
            msgBox.exec()
            if msgBox.clickedButton() == yesButton:
                event.accept()
            else:
                event.ignore()
        else:       
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("是否要退出程序？")
            msgBox.setWindowTitle(self.conf.ConfigSectionMap('App')['mainwindowtitle'])
            yesButton = msgBox.addButton('是', QMessageBox.YesRole)
            msgBox.addButton('否',QMessageBox.NoRole)          
            
            msgBox.exec()
            if msgBox.clickedButton() == yesButton:
                event.accept()
            else:
                event.ignore()

    def restoreUI(self):
        ''' 
            恢复界面原始状态
        '''
        self.batchStart = False
        self.batchDetInRunning = False
        self.progressBar.reset()

    def brightnessAndContrastAdjust(self):
        '''
            actionImageAdjust:图像调整界面
        '''
        if self.brightnessAndContrastAdjustWindow is None:
            self.brightnessAndContrastAdjustWindow = BrightnessAndContrastAdjustWindow()
            self.brightnessAndContrastAdjustWindow.brightness_contrast_params_signal.connect(self.imageAdjust)
        self.brightnessAndContrastAdjustWindow.show()
        
    def imageAdjust(self, alpha, beta):
        print('alpha:{}, beta:{}'.format(alpha, beta))
        # 获取图像
        # self.oriImage = self.ui.imageView.pixmapItem.pixmap().toImage()  
        qImage = self.oriQImage.convertToFormat(QImage.Format.Format_RGB888)      
        # 图像的np存储形式
        width , height = qImage.size().width(), qImage.size().height()
        ptr = qImage.bits()
        ptr.setsize(height * width * 3)
        img_np = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        # 调整，原理：IMG_out(i,j) = alpha*IMG_in(i,j) + beta       
        new_image = np.zeros(img_np.shape, img_np.dtype)
        new_image = cv2.convertScaleAbs(img_np, alpha=alpha, beta=beta)

        # 转成QImage
        # print(new_image.shape)
        height, width, bytesPerComponent = new_image.shape
        bytesPerLine = 3 * width
        qImg = QImage(new_image.data, width, height, bytesPerLine,
                       QImage.Format_RGB888)
        qImg = qImg.rgbSwapped()        

        self.ui.imageView.pixmapItem.setPixmap(QPixmap.fromImage(qImg))
        
        # cv2.imshow('img', img_np)
        # cv2.waitKey()
        # print(type(qImage))

    def configure(self):
        '''
            actionSetup:配置参数界面
        '''
               
        # 通过配置文件加载配置参数界面
        self.conf.reloadIniFile(config.iniFile)
        configWindow = ConfigureWindow() 
        # 信号处理
        configWindow.config_signal.connect(self.configSignalCompleted)
        self.loadConfToUI(configWindow)
        retCode = configWindow.exec()
        # print(retCode)
        self.conf.reloadIniFile(config.iniFile)  
        # 清空当前界面
        self.ui.imageView.loadPicFile('')
        self.ui.listWidgetCropImages.clear()
        self.progressBar.reset()      

    def configSignalCompleted(self):
        '''
            完成参数设置，根据设置修改界面
        '''

        # 状态栏显示参数    
        odConfig = ODConfig(config.iniFile)
        detectionMode = int(odConfig.ConfigSectionMap('App')['detectionmode'])
        detectWinSize = odConfig.ConfigSectionMap('App')['detectionwindowsize']
        nms = odConfig.ConfigSectionMap('App')['nms']
        loadDetectResultPath = odConfig.ConfigSectionMap('App')['loadresultpath']

        if int(detectionMode) == 2:
            self.ui.statusbar.showMessage('检测模式: {}, 检测结果载入路径: {} '.format('结果载入',loadDetectResultPath))
        elif int(detectionMode) == 0:
            self.ui.statusbar.showMessage('检测模式: {}, 检测窗口大小: {} , NMS: {}'.format('逐张检测',detectWinSize, nms))
        else:
            self.ui.statusbar.showMessage('检测模式: {}, 检测窗口大小: {} , NMS: {}'.format('批量检测',detectWinSize, nms))

        if detectionMode == 0 :  #逐张检测
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)
        elif detectionMode == 1 :  #批量检测
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)         
               
        elif detectionMode == 2 :   #加载检测结果
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)
        else:
            pass

    def loadConfToUI(self,confWindow):
        '''
            读取配置文件内容，加载到配置窗口中
        ''' 
        # 检测模式((0:逐张检测， 1：批量将测， 2：加载检测结果))
        detectionMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detectionMode == 0:
            confWindow.ui.radioButtonSingleDetectMode.setChecked(True)
        elif detectionMode == 1:
            confWindow.ui.radioButtonBatchDetectMode.setChecked(True)
        elif detectionMode == 2:
            confWindow.ui.radioButtonLoadDetectResult.setChecked(True)
        else :
            pass
        
        # 检测参数
        confWindow.ui.lineEditDetectWindowSize.setText(self.conf.ConfigSectionMap('App')['detectionwindowsize'])
        confWindow.ui.lineEditNMS.setText(self.conf.ConfigSectionMap('App')['nms'])

        # 路径设置
        confWindow.ui.lineEditInputPath.setText(self.conf.ConfigSectionMap('App')['inputrootimagepath'])
        confWindow.ui.lineEditOutPutPath.setText(self.conf.ConfigSectionMap('App')['outputrootresult'])

        confWindow.ui.lineEditDetectResult.setText(self.conf.ConfigSectionMap('App')['loadresultpath'])

    def showOrHideLog(self):   
        '''
            actionDisplayLog:日志显示
        '''     
        # 日志窗口
        if self.ui.dockWidgetLog.isVisible():
            self.ui.dockWidgetLog.setVisible(False)
        else:
            # 让日志窗口位于主窗口边缘内部
            win_x = self.geometry().x()
            win_y = self.geometry().y()
            win_width = self.geometry().width()
            self.ui.dockWidgetLog.setGeometry(
                        win_x + win_width - self.ui.dockWidgetLog.geometry().width(), 
                        win_y + 250,                         
                        self.ui.dockWidgetLog.geometry().width(),
                        self.ui.dockWidgetLog.geometry().height()
                    )            
            self.ui.dockWidgetLog.setVisible(True)           

    def startDetection(self):
        '''
            actionStart
        '''                   

        # 更新工具栏按钮状态 
        detectionMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detectionMode == 0 :  #逐张检测
            self.ui.actionStart.setEnabled(False)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(True)
            self.ui.actionPrev.setEnabled(True)
            self.ui.actionRedo.setEnabled(True)
            self.ui.actionImageAdjust.setEnabled(True)

            self.ui.plainTextEditLog.clear()

            # 统计总数
            inputRootImagePath = self.conf.ConfigSectionMap('App')['inputrootimagepath']
            resultOutputPath = self.conf.ConfigSectionMap('App')['outputrootresult']
            totalProgress = 0
            for root, dirs, files in os.walk(inputRootImagePath):
                for fileName in files:
                    if fileName[fileName.rfind('.'):].upper() == '.JPG':
                        # self.allImageFiles.append(os.path.join(root, fileName))
                        self.allImageFiles.append(Path(root).joinpath(fileName).as_posix())
                        totalProgress +=1
            

            if totalProgress == 0:
                self.ui.actionStart.setEnabled(False)
                self.ui.actionNext.setEnabled(False)
                self.ui.actionPrev.setEnabled(False)
                self.ui.actionRedo.setEnabled(False)
                self.ui.actionImageAdjust.setEnabled(False)
                self.ui.statusbar.showMessage('目录下没有可检测的图像。')
            else:
                # 设置进度条
                self.progressBar.setMinimum(0)
                self.progressBar.setMaximum(totalProgress)  
                # 此处检测第一张
                self.SD = singleDetection(inputRootImagePath=inputRootImagePath,resultOutputPath=resultOutputPath)  
                resultJsonFile = self.SD.detect(self.allImageFiles[0])           
                
                
                self.currentImgIndex = 0
                # time.sleep(1)
                self.progressBar.setValue(1)
                self.ui.plainTextEditLog.appendPlainText(self.allImageFiles[0])

                # 加载结果
                self.loadDetectResult(resultJsonFile)
                
                # 设置QImage
                self.oriQImage = self.ui.imageView.pixmapItem.pixmap().toImage()
            


        elif detectionMode == 1 :  #批量检测            

            if self.batchStart: #不是第一次点击，发送resume信号
                # 发送继续信号
                self.batchStart = True
                self.batchDetectionSignal.emit(MSG_RESUME)                
            else: #第一次点击
                
                self.ui.plainTextEditLog.clear()
                # 统计总数
                inputRootImagePath = self.conf.ConfigSectionMap('App')['inputrootimagepath']
                resultOutputPath = self.conf.ConfigSectionMap('App')['outputrootresult']
                totalProgress = 0
                for root, dirs, files in os.walk(inputRootImagePath):
                    for fileName in files:
                        if fileName[fileName.rfind('.'):].upper() == '.JPG':
                            self.allImageFiles.append(Path(root).joinpath(fileName).as_posix())
                            totalProgress +=1

                if totalProgress == 0:                    
                    self.ui.statusbar.showMessage('目录下没有可检测的图像。') 
                else:
                    self.ui.actionStart.setEnabled(False)
                    self.ui.actionPause.setEnabled(True)
                    self.ui.actionStop.setEnabled(True)
                    self.ui.actionNext.setEnabled(False)
                    self.ui.actionPrev.setEnabled(False)
                    self.ui.actionRedo.setEnabled(False)
                    self.ui.actionImageAdjust.setEnabled(False)
                    self.ui.actionSetup.setEnabled(False)

                    self.batchDetInRunning = True
                    self.batchStart = True
                    # 设置进度条
                    self.progressBar.setMinimum(1)
                    self.progressBar.setMaximum(totalProgress)
                    # self.ui.statusbar.showMessage('批量检测...')
                    # 启动进程开始批量检测                    
                    t = batchDetectionThread(self,inputRootImagePath=inputRootImagePath, resultOutputPath=resultOutputPath)
                    t.change_progress.connect(self.changeProgress)
                    t.start()  
               
        elif detectionMode == 2 :   #加载检测结果
            self.ui.actionStart.setEnabled(False)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(True)
            self.ui.actionPrev.setEnabled(True)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(True)

            self.ui.plainTextEditLog.clear()

            # 统计总数
            loadResultPath = self.conf.ConfigSectionMap('App')['loadresultpath']
            totalProgress = 0
            for root, dirs, files in os.walk(loadResultPath):
                for fileName in files:
                    if fileName[fileName.rfind('.'):].upper() == '.JSON':
                        self.allAnnoFiles.append(Path(root).joinpath(fileName).as_posix())
                        # self.allAnnoFiles.append(os.path.join(root, fileName))
                        totalProgress +=1
            

            if totalProgress == 0:
                self.ui.actionStart.setEnabled(False)
                self.ui.actionNext.setEnabled(False)
                self.ui.actionPrev.setEnabled(False)
                self.ui.actionRedo.setEnabled(False)
                self.ui.actionImageAdjust.setEnabled(False)
                self.ui.statusbar.showMessage('目录下没有检测结果。')
            else:
                # 设置进度条
                self.progressBar.setMinimum(0)
                self.progressBar.setMaximum(totalProgress)               
                
                # 此处加载第一张
                self.currentImgIndex = 0
                fName = self.loadDetectResult(self.allAnnoFiles[self.currentImgIndex])
                self.progressBar.setValue(1)
                self.ui.plainTextEditLog.appendPlainText(fName)

                # 设置QImage
                self.oriQImage = self.ui.imageView.pixmapItem.pixmap().toImage()
        else:
            pass          

    def changeProgress(self, i, s1, s2):
        # 处理从线程收到的信号
        if s1 == MSG_FINISHED: #完成检测，更新界面状态
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)
            self.ui.actionSetup.setEnabled(True)

            self.restoreUI()
        else:
            self.loadDetectResult(s2)
            self.progressBar.setValue(self.progressBar.value() + i)
            self.ui.plainTextEditLog.appendPlainText(s1)
        

    def pauseDetection(self):
        '''
            actionPause
        '''               
        # 更新工具栏按钮状态
        detectionMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detectionMode == 0 :  #逐张检测
            pass
        elif detectionMode == 1 :  #批量检测
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)
        else:  #加载检测结果
            pass

        
        # 发送暂停信号
        self.batchDetectionSignal.emit(MSG_PAUSE)
        
        

    def stopDetection(self):
        '''
            actionStop
        '''
        # 更新工具栏按钮状态
        detectionMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detectionMode == 0 :  #逐张检测
            pass
        elif detectionMode == 1 :  #批量检测
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)
            self.ui.actionSetup.setEnabled(True)

            # 向批量检测进程发送stop信号
            print('sending stop signal...')
            self.restoreUI()
            self.batchDetectionSignal.emit(MSG_STOP)

            
            
        else:  #加载检测结果
            pass      
        
        

    def nextImage(self):  
        detectionMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detectionMode == 0:  #逐张检测
            totalFileCount = len(self.allImageFiles)            
            if self.currentImgIndex + 1 == totalFileCount:
                self.ui.statusbar.showMessage('已到最后一张。')
                self.ui.actionNext.setEnabled(False)                
            else:
                self.currentImgIndex += 1
                # 检测下一张
                # time.sleep(0.1)
                resultJsonFile =  self.SD.detect(self.allImageFiles[self.currentImgIndex])
                self.progressBar.setValue(self.progressBar.value() + 1)
                self.ui.plainTextEditLog.appendPlainText(self.allImageFiles[self.currentImgIndex])

                # 加载结果
                self.loadDetectResult(resultJsonFile)

                # 设置QImage
                self.oriQImage = self.ui.imageView.pixmapItem.pixmap().toImage()
            if self.currentImgIndex != 0:
                self.ui.actionPrev.setEnabled(True)
        elif detectionMode == 2:  #加载检测结果
            totalFileCount = len(self.allAnnoFiles)            
            if self.currentImgIndex + 1 == totalFileCount:
                self.ui.statusbar.showMessage('已到最后一张。')
                self.ui.actionNext.setEnabled(False)                
            else:
                self.currentImgIndex += 1
                # 加载下一张
                # time.sleep(0.1)
                self.loadDetectResult(self.allAnnoFiles[self.currentImgIndex])

                self.progressBar.setValue(self.progressBar.value() + 1)
                self.ui.plainTextEditLog.appendPlainText(self.allAnnoFiles[self.currentImgIndex])
                # 设置QImage
                self.oriQImage = self.ui.imageView.pixmapItem.pixmap().toImage()
            if self.currentImgIndex != 0:
                self.ui.actionPrev.setEnabled(True)


    def prevImage(self):
        detectionMode = int(self.conf.ConfigSectionMap('App')['detectionmode'])
        if detectionMode == 0:  #逐张检测
            totalFileCount = len(self.allImageFiles)            
            if self.currentImgIndex == 0:
                self.ui.statusbar.showMessage('已到第一张。')
                self.ui.actionPrev.setEnabled(False)
            else:
                self.currentImgIndex -= 1
                # 检测上一张
                # time.sleep(0.1)
                resultJsonFile = self.SD.detect(self.allImageFiles[self.currentImgIndex])
                self.progressBar.setValue(self.progressBar.value() - 1)
                self.ui.plainTextEditLog.appendPlainText(self.allImageFiles[self.currentImgIndex])

                # 加载结果
                self.loadDetectResult(resultJsonFile)

                # 设置QImage
                self.oriQImage = self.ui.imageView.pixmapItem.pixmap().toImage()

            if self.currentImgIndex != totalFileCount - 1:
                self.ui.actionNext.setEnabled(True)
        elif detectionMode == 2:  #加载检测结果
            totalFileCount = len(self.allAnnoFiles)            
            if self.currentImgIndex == 0:
                self.ui.statusbar.showMessage('已到第一张。')
                self.ui.actionPrev.setEnabled(False)
            else:
                self.currentImgIndex -= 1
                # 加载上一张
                # time.sleep(0.1)
                self.loadDetectResult(self.allAnnoFiles[self.currentImgIndex])

                self.progressBar.setValue(self.progressBar.value() - 1)
                self.ui.plainTextEditLog.appendPlainText(self.allAnnoFiles[self.currentImgIndex])

                # 设置QImage
                self.oriQImage = self.ui.imageView.pixmapItem.pixmap().toImage()

            if self.currentImgIndex != totalFileCount - 1:
                self.ui.actionNext.setEnabled(True)


    def loadDetectResult(self,annoFile):
        '''
            从annoFile文件中读取内容加载到界面中
            返回：加载图像的文件名
        '''
        # annoFile = self.allAnnoFiles[self.currentImgIndex]
        dr = DetectResult(annoJsonFile=annoFile)
        # 清空crop列表
        self.ui.listWidgetCropImages.clear()
        self.cropImages = []               
        
        imgFile = dr.getImageFileName()
        # print(imgFile)
        annoRects = dr.getImageAnnos()
        # 加载图像和标注
        self.ui.imageView.loadPicFile(imgFile)
        self.ui.imageView.loadAnnoRects(annoRects)   
        self.ui.imageView.fitInView()
        # 加载crop图像        
        img = cv2.imread(imgFile)
        
        for shape in annoRects:
            self.cropImages.append({
                "id": shape['id'],
                "className": shape['className'],
                "score": shape['score'],
                # crop_img = img[y:y+height, x:x+width]
                'crop_image': img[shape['shape'][1]:shape['shape'][3], shape['shape'][0]: shape['shape'][2]]
            })
        
        for cropImg in self.cropImages:
            item = QListWidgetItem(cropImg['className'] + '_{}'.format(cropImg['score']))  
            # 保存id值 
            item.setData(QtCore.Qt.UserRole, cropImg['id'])     
            icon = QIcon()
            # crop图像
            img = cropImg['crop_image']

            height, width, bytesPerComponent = img.shape
            bytesPerLine = 3 * width
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)               
            # 注意此处的copy()
            qImg = QImage(img.copy(), width, height, bytesPerLine,QImage.Format_RGB888)
            # 通过icon显示crop的图像
            icon.addPixmap(QPixmap.fromImage(qImg),QIcon.Normal, QIcon.Off)
            item.setIcon(icon)
            self.ui.listWidgetCropImages.addItem(item) 

        return imgFile


def checkCaffeEnv():
    '''
        检查系统caffe环境
        返回：0-没有问题  1-有问题 
    '''        
    try:
        import sys        
        sys.path.append(Path(config.caffe_root).joinpath('python').as_posix())
        import caffe
        ret = 0
        return ret
    except:
        ret = 1
        return ret 

def checkSysParams():
    '''
        检查系统参数是否完备
        返回：0-没有问题  1-有问题
    '''
    iniConf = configparser.ConfigParser()
    iniConf.read(config.iniFile, encoding='utf-8')
    paramsInIniFileSet = set(iniConf.options('App'))
    paramsInConfigFileSet = set(config.runningParams)

    if paramsInIniFileSet.issubset(paramsInConfigFileSet):
        return 0

    return 1        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pixmap = QPixmap('./resources/splash.jpg')
    splashScreen = QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
    splashScreen.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splashScreen.setEnabled(False)
    splashScreen.show()
   
    # 正式运行请取消下面注释
    # splashScreen.showMessage('正在检查系统caffe环境......')
    # ret = checkCaffeEnv()
    # if ret == 1:
    #     splashScreen.showMessage('caffe环境有误,请检查后重试。即将退出......')
    #     time.sleep(2)
    #     sys.exit()
    # splashScreen.showMessage('caffe环境检查完毕！')

    # app.processEvents()
    
    splashScreen.showMessage('正在检查系统运行参数......')
    ret = checkSysParams()
    if ret == 1:
        splashScreen.showMessage('系统参数有误,请检查后重试。即将退出......')
        time.sleep(2)
        sys.exit()
    splashScreen.showMessage('系统运行参数检查完毕！')

    app.processEvents()

    splashScreen.showMessage('正在加载模型......')
    # 用于检测的caffe网络模型
    DN = DetectionNet()
    time.sleep(2)    
    splashScreen.showMessage('加载模型完毕！')

    app.processEvents()

    w = ObjectDetectionMainWindow()
    w.show()

    splashScreen.finish(w)

    sys.exit(app.exec_())