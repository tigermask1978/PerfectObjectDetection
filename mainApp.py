import sys
import os
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

from mainWindow import *
from configureWindow import *
import config
from utils import ODConfig
import configparser

# 批量检测发送信号消息
MSG_PAUSE = 'pause'
MSG_RESUME = 'resume'
MSG_STOP = 'stop'
MSG_FINISHED = 'finished'
# 配置窗口发送信号
MSG_CONF_COMPLETED = 'completed'

class batchDetectionThread(QtCore.QThread):
    '''
        批量检测子进程
    '''
    # 进度信号
    change_progress = QtCore.pyqtSignal(int,str)

    def __init__(self, parent=None, inputRootImagePath=None):
        QtCore.QThread.__init__(self, parent)
        # 批量检测图像根目录
        self.inputRootImagePath = inputRootImagePath     

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
        for root, dirs, files in os.walk(self.inputRootImagePath):
            for fileName in files:
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

                if fileName[fileName.rfind('.'):].upper() == '.JPG':                   
                    time.sleep(0.1)
                    fileNameWithFullPath = os.path.join(root, fileName)
                    print(fileNameWithFullPath)
                    # 处理完一张，发送消息更新进度条和界面
                    self.change_progress.emit(1, fileNameWithFullPath)  
            else:
                continue
            break      
        #完成批量检测
        self.change_progress.emit(1, MSG_FINISHED)     

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
        

        # 批量检测标志(True标识已经开始批量检测，开始按钮不是第一次点击)
        self.batchStart = False
        # 是否批量检测中
        self.batchDetInRunning = False 

        # 逐张检测
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
        # 调用系统的close事件(执行的是closeEvent)
        self.ui.actionExit.triggered.connect(self.close)

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
            totalProgress = 0
            for root, dirs, files in os.walk(inputRootImagePath):
                for fileName in files:
                    if fileName[fileName.rfind('.'):].upper() == '.JPG':
                        self.allImageFiles.append(os.path.join(root, fileName))
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
                self.currentImgIndex = 0
                time.sleep(1)
                self.progressBar.setValue(1)
                self.ui.plainTextEditLog.appendPlainText(self.allImageFiles[0])
                
            


        elif detectionMode == 1 :  #批量检测
            self.ui.actionStart.setEnabled(False)
            self.ui.actionPause.setEnabled(True)
            self.ui.actionStop.setEnabled(True)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)
            self.ui.actionSetup.setEnabled(False)

            self.batchDetInRunning = True

            if self.batchStart: #不是第一次点击，发送resume信号
                # 发送继续信号
                self.batchStart = True
                self.batchDetectionSignal.emit(MSG_RESUME)                
            else: #第一次点击
                self.batchStart = True
                self.ui.plainTextEditLog.clear()
                # 统计总数
                inputRootImagePath = self.conf.ConfigSectionMap('App')['inputrootimagepath']
                totalProgress = 0
                for root, dirs, files in os.walk(inputRootImagePath):
                    for fileName in files:
                        if fileName[fileName.rfind('.'):].upper() == '.JPG':
                            totalProgress +=1
                # 设置进度条
                self.progressBar.setMinimum(1)
                self.progressBar.setMaximum(totalProgress)
                # self.ui.statusbar.showMessage('批量检测...')
                # 启动进程开始批量检测
                t = batchDetectionThread(self,inputRootImagePath=inputRootImagePath)
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
                        self.allAnnoFiles.append(os.path.join(root, fileName))
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
                time.sleep(1)
                self.progressBar.setValue(1)
                self.ui.plainTextEditLog.appendPlainText(self.allAnnoFiles[0])
        else:
            pass          

    def changeProgress(self, i, s):
        # 处理从线程收到的信号
        if s == MSG_FINISHED: #完成检测，更新界面状态
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
            self.progressBar.setValue(self.progressBar.value() + i)
            self.ui.plainTextEditLog.appendPlainText(s)
        


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
                time.sleep(0.1)
                self.progressBar.setValue(self.progressBar.value() + 1)
                self.ui.plainTextEditLog.appendPlainText(self.allImageFiles[self.currentImgIndex])
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
                time.sleep(0.1)
                self.progressBar.setValue(self.progressBar.value() + 1)
                self.ui.plainTextEditLog.appendPlainText(self.allAnnoFiles[self.currentImgIndex])
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
                time.sleep(0.1)
                self.progressBar.setValue(self.progressBar.value() - 1)
                self.ui.plainTextEditLog.appendPlainText(self.allImageFiles[self.currentImgIndex])

            if self.currentImgIndex != totalFileCount - 1:
                self.ui.actionNext.setEnabled(True)
        elif detectionMode == 2:  #加载检测结果
            totalFileCount = len(self.allAnnoFiles)            
            if self.currentImgIndex == 0:
                self.ui.statusbar.showMessage('已到第一张。')
                self.ui.actionPrev.setEnabled(False)
            else:
                self.currentImgIndex -= 1
                # 检测上一张
                time.sleep(0.1)
                self.progressBar.setValue(self.progressBar.value() - 1)
                self.ui.plainTextEditLog.appendPlainText(self.allAnnoFiles[self.currentImgIndex])

            if self.currentImgIndex != totalFileCount - 1:
                self.ui.actionNext.setEnabled(True)


def checkCaffeEnv():
    '''
        检查系统caffe环境
        返回：0-没有问题  1-有问题 
    '''
    ret = 0
    try:
        import caffe
    except:
        ret = 1
    
    try:
        import sys
        sys.path.append(os.path.join(config.caffe_root,'python'))
        import caffe
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
    time.sleep(2)
    splashScreen.showMessage('加载模型完毕！')

    app.processEvents()

    w = ObjectDetectionMainWindow()
    w.show()

    splashScreen.finish(w)

    sys.exit(app.exec_())