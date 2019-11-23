# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configureWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogConfig(object):
    def setupUi(self, DialogConfig):
        DialogConfig.setObjectName("DialogConfig")
        DialogConfig.resize(594, 566)
        DialogConfig.setMinimumSize(QtCore.QSize(500, 500))
        DialogConfig.setMaximumSize(QtCore.QSize(16777215, 600))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/setup.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogConfig.setWindowIcon(icon)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(DialogConfig)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.groupBoxMode = QtWidgets.QGroupBox(DialogConfig)
        self.groupBoxMode.setObjectName("groupBoxMode")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBoxMode)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.radioButtonSingleDetectMode = QtWidgets.QRadioButton(self.groupBoxMode)
        self.radioButtonSingleDetectMode.setObjectName("radioButtonSingleDetectMode")
        self.horizontalLayout.addWidget(self.radioButtonSingleDetectMode)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.radioButtonBatchDetectMode = QtWidgets.QRadioButton(self.groupBoxMode)
        self.radioButtonBatchDetectMode.setObjectName("radioButtonBatchDetectMode")
        self.horizontalLayout.addWidget(self.radioButtonBatchDetectMode)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.radioButtonLoadDetectResult = QtWidgets.QRadioButton(self.groupBoxMode)
        self.radioButtonLoadDetectResult.setObjectName("radioButtonLoadDetectResult")
        self.horizontalLayout.addWidget(self.radioButtonLoadDetectResult)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.groupBoxMode, 0, 0, 1, 1)
        self.groupBoxDetectParams = QtWidgets.QGroupBox(DialogConfig)
        self.groupBoxDetectParams.setObjectName("groupBoxDetectParams")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBoxDetectParams)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.groupBoxDetectParams)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.lineEditDetectWindowSize = QtWidgets.QLineEdit(self.groupBoxDetectParams)
        self.lineEditDetectWindowSize.setMaxLength(32767)
        self.lineEditDetectWindowSize.setObjectName("lineEditDetectWindowSize")
        self.horizontalLayout_3.addWidget(self.lineEditDetectWindowSize)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.groupBoxDetectParams)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.lineEditNMS = QtWidgets.QLineEdit(self.groupBoxDetectParams)
        self.lineEditNMS.setObjectName("lineEditNMS")
        self.horizontalLayout_4.addWidget(self.lineEditNMS)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.gridLayout.addWidget(self.groupBoxDetectParams, 1, 0, 1, 1)
        self.groupBoxPathSelect = QtWidgets.QGroupBox(DialogConfig)
        self.groupBoxPathSelect.setObjectName("groupBoxPathSelect")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBoxPathSelect)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.groupBoxPathSelect)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.lineEditInputPath = QtWidgets.QLineEdit(self.groupBoxPathSelect)
        self.lineEditInputPath.setObjectName("lineEditInputPath")
        self.horizontalLayout_6.addWidget(self.lineEditInputPath)
        self.pushButtonPathSelect4Input = QtWidgets.QPushButton(self.groupBoxPathSelect)
        self.pushButtonPathSelect4Input.setMinimumSize(QtCore.QSize(40, 0))
        self.pushButtonPathSelect4Input.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButtonPathSelect4Input.setObjectName("pushButtonPathSelect4Input")
        self.horizontalLayout_6.addWidget(self.pushButtonPathSelect4Input)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_4 = QtWidgets.QLabel(self.groupBoxPathSelect)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_7.addWidget(self.label_4)
        self.lineEditOutPutPath = QtWidgets.QLineEdit(self.groupBoxPathSelect)
        self.lineEditOutPutPath.setObjectName("lineEditOutPutPath")
        self.horizontalLayout_7.addWidget(self.lineEditOutPutPath)
        self.pushButtonPathSelect4Output = QtWidgets.QPushButton(self.groupBoxPathSelect)
        self.pushButtonPathSelect4Output.setMinimumSize(QtCore.QSize(40, 0))
        self.pushButtonPathSelect4Output.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButtonPathSelect4Output.setObjectName("pushButtonPathSelect4Output")
        self.horizontalLayout_7.addWidget(self.pushButtonPathSelect4Output)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.gridLayout.addWidget(self.groupBoxPathSelect, 2, 0, 1, 1)
        self.groupBoxDetectResult = QtWidgets.QGroupBox(DialogConfig)
        self.groupBoxDetectResult.setObjectName("groupBoxDetectResult")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.groupBoxDetectResult)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_5 = QtWidgets.QLabel(self.groupBoxDetectResult)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_9.addWidget(self.label_5)
        self.lineEditDetectResult = QtWidgets.QLineEdit(self.groupBoxDetectResult)
        self.lineEditDetectResult.setObjectName("lineEditDetectResult")
        self.horizontalLayout_9.addWidget(self.lineEditDetectResult)
        self.pushButtonPathSelect4DetectResult = QtWidgets.QPushButton(self.groupBoxDetectResult)
        self.pushButtonPathSelect4DetectResult.setMinimumSize(QtCore.QSize(40, 0))
        self.pushButtonPathSelect4DetectResult.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButtonPathSelect4DetectResult.setObjectName("pushButtonPathSelect4DetectResult")
        self.horizontalLayout_9.addWidget(self.pushButtonPathSelect4DetectResult)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_9)
        self.gridLayout.addWidget(self.groupBoxDetectResult, 3, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem4)
        self.pushButtonOk = QtWidgets.QPushButton(DialogConfig)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.horizontalLayout_8.addWidget(self.pushButtonOk)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem5)
        self.pushButtonCancel = QtWidgets.QPushButton(DialogConfig)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout_8.addWidget(self.pushButtonCancel)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem6)
        self.gridLayout.addLayout(self.horizontalLayout_8, 4, 0, 1, 1)
        self.horizontalLayout_11.addLayout(self.gridLayout)

        self.retranslateUi(DialogConfig)
        QtCore.QMetaObject.connectSlotsByName(DialogConfig)

    def retranslateUi(self, DialogConfig):
        _translate = QtCore.QCoreApplication.translate
        DialogConfig.setWindowTitle(_translate("DialogConfig", "检测参数设置"))
        self.groupBoxMode.setTitle(_translate("DialogConfig", "工作模式"))
        self.radioButtonSingleDetectMode.setText(_translate("DialogConfig", "逐张检测"))
        self.radioButtonBatchDetectMode.setText(_translate("DialogConfig", "批量检测"))
        self.radioButtonLoadDetectResult.setText(_translate("DialogConfig", "加载结果"))
        self.groupBoxDetectParams.setTitle(_translate("DialogConfig", "检测参数"))
        self.label.setText(_translate("DialogConfig", " 检测窗口大小(1-5000):"))
        self.label_2.setText(_translate("DialogConfig", "         NMS(0.3-0.5):"))
        self.groupBoxPathSelect.setTitle(_translate("DialogConfig", "路径设置"))
        self.label_3.setText(_translate("DialogConfig", "输入路径："))
        self.pushButtonPathSelect4Input.setText(_translate("DialogConfig", "..."))
        self.label_4.setText(_translate("DialogConfig", "输出路径："))
        self.pushButtonPathSelect4Output.setText(_translate("DialogConfig", "..."))
        self.groupBoxDetectResult.setTitle(_translate("DialogConfig", "检测结果"))
        self.label_5.setText(_translate("DialogConfig", "路径："))
        self.pushButtonPathSelect4DetectResult.setText(_translate("DialogConfig", "..."))
        self.pushButtonOk.setText(_translate("DialogConfig", "确定"))
        self.pushButtonCancel.setText(_translate("DialogConfig", "取消"))
