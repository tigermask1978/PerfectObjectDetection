import sys
import os
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

from mainWindow import *
from configureWindow import *
import config

# 批量检测发送信号消息
MSG_PAUSE = 'pause'
MSG_RESUME = 'resume'
MSG_STOP = 'stop'
MSG_FINISHED = 'finished'

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
    def __init__(self):
        super().__init__()

        self.ui = Ui_DialogConfig()
        self.ui.setupUi(self)

        self.initWindow()

    def initWindow(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        

        


class ObjectDetectionMainWindow(QMainWindow):  
    
    batchDetectionSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        

        # 将进度条加入状态栏 
        self.progressBar = QProgressBar()  
        self.ui.statusbar.addPermanentWidget(self.progressBar)  

        # 批量检测标志(True标识已经开始批量检测，开始按钮不是第一次点击)
        self.batchStart = False
        # 是否批量检测中
        self.batchDetInRunning = False 
                

        self.setUI()

    def setUI(self):
        # 主窗口标题
        self.setWindowTitle(config.MainWindowTitle)
        # 左侧显示工具栏
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.ui.toolBar)    
        # 工具栏按钮初始状态
        self.ui.actionStart.setEnabled(True)
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

        # Actions
        self.ui.actionSetup.triggered.connect(self.configure)
        self.ui.actionDisplayLog.triggered.connect(self.showOrHideLog)
        self.ui.actionStart.triggered.connect(self.startDetection)
        self.ui.actionPause.triggered.connect(self.pauseDetection)
        self.ui.actionStop.triggered.connect(self.stopDetection)
        self.ui.actionNext.triggered.connect(self.nextImage)  
        # 调用系统的close事件(执行的是closeEvent)
        self.ui.actionExit.triggered.connect(self.close)

    def closeEvent(self, event):
        # 重写主窗口的close事件，加入关闭逻辑
        if self.batchDetInRunning:  #批量检测进程运行中
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText("正在检测中，退出将终止现有检测，是否继续退出？")
            msgBox.setWindowTitle(config.MainWindowTitle)
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
            msgBox.setWindowTitle(config.MainWindowTitle)
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
        configWindow = ConfigureWindow()
        configWindow.exec()
        

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
        if config.DetectionMode == 0 :  #逐张检测
            self.ui.actionStart.setEnabled(False)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(True)
            self.ui.actionPrev.setEnabled(True)
            self.ui.actionRedo.setEnabled(True)
            self.ui.actionImageAdjust.setEnabled(True)
        elif config.DetectionMode == 1 :  #批量检测
            self.ui.actionStart.setEnabled(False)
            self.ui.actionPause.setEnabled(True)
            self.ui.actionStop.setEnabled(True)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)

            self.batchDetInRunning = True

            if self.batchStart: #不是第一次点击，发送resume信号
                # 发送继续信号
                self.batchStart = True
                self.batchDetectionSignal.emit(MSG_RESUME)                
            else: #第一次点击
                self.batchStart = True
                # 统计总数
                inputRootImagePath = config.InputRootImagePath
                totalProgress = 0
                for root, dirs, files in os.walk(inputRootImagePath):
                    for fileName in files:
                        if fileName[fileName.rfind('.'):].upper() == '.JPG':
                            totalProgress +=1
                # 设置进度条
                self.progressBar.setMinimum(1)
                self.progressBar.setMaximum(totalProgress)
                self.ui.statusbar.showMessage('批量检测...')
                # 启动进程开始批量检测
                t = batchDetectionThread(self,inputRootImagePath=inputRootImagePath)
                t.change_progress.connect(self.changeProgress)
                t.start()  
               
        elif config.DetectionMode == 2 :   #加载检测结果
            self.ui.actionStart.setEnabled(False)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(True)
            self.ui.actionPrev.setEnabled(True)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(True)
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

            self.restoreUI()
        else:
            self.progressBar.setValue(self.progressBar.value() + i)
            self.ui.plainTextEditLog.appendPlainText(s)
        


    def pauseDetection(self):
        '''
            actionPause
        '''               
        # 更新工具栏按钮状态
        if config.DetectionMode == 0 :  #逐张检测
            pass
        elif config.DetectionMode == 1 :  #批量检测
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
        if config.DetectionMode == 0 :  #逐张检测
            pass
        elif config.DetectionMode == 1 :  #批量检测
            self.ui.actionStart.setEnabled(True)
            self.ui.actionPause.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionNext.setEnabled(False)
            self.ui.actionPrev.setEnabled(False)
            self.ui.actionRedo.setEnabled(False)
            self.ui.actionImageAdjust.setEnabled(False)

            # 向批量检测进程发送stop信号
            print('sending stop signal...')
            self.restoreUI()
            self.batchDetectionSignal.emit(MSG_STOP)

            
            
        else:  #加载检测结果
            pass      
        
        

    def nextImage(self):  
        pass
 

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ObjectDetectionMainWindow()
    w.show()
    sys.exit(app.exec_())