# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'brightnessAndContrastAdjustWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogBrightnessAndContrastAdjust(object):
    def setupUi(self, DialogBrightnessAndContrastAdjust):
        DialogBrightnessAndContrastAdjust.setObjectName("DialogBrightnessAndContrastAdjust")
        DialogBrightnessAndContrastAdjust.resize(326, 150)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(DialogBrightnessAndContrastAdjust)
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(DialogBrightnessAndContrastAdjust)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.horizontalSliderBrightness = QtWidgets.QSlider(DialogBrightnessAndContrastAdjust)
        self.horizontalSliderBrightness.setMinimum(0)
        self.horizontalSliderBrightness.setMaximum(510)
        self.horizontalSliderBrightness.setProperty("value", 255)
        self.horizontalSliderBrightness.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSliderBrightness.setObjectName("horizontalSliderBrightness")
        self.horizontalLayout.addWidget(self.horizontalSliderBrightness)
        self.spinBoxBrightness = QtWidgets.QSpinBox(DialogBrightnessAndContrastAdjust)
        self.spinBoxBrightness.setMinimum(0)
        self.spinBoxBrightness.setMaximum(510)
        self.spinBoxBrightness.setProperty("value", 255)
        self.spinBoxBrightness.setObjectName("spinBoxBrightness")
        self.horizontalLayout.addWidget(self.spinBoxBrightness)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(DialogBrightnessAndContrastAdjust)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.horizontalSliderContrast = QtWidgets.QSlider(DialogBrightnessAndContrastAdjust)
        self.horizontalSliderContrast.setMinimum(0)
        self.horizontalSliderContrast.setMaximum(254)
        self.horizontalSliderContrast.setProperty("value", 127)
        self.horizontalSliderContrast.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSliderContrast.setObjectName("horizontalSliderContrast")
        self.horizontalLayout_2.addWidget(self.horizontalSliderContrast)
        self.spinBoxContrast = QtWidgets.QSpinBox(DialogBrightnessAndContrastAdjust)
        self.spinBoxContrast.setMinimum(0)
        self.spinBoxContrast.setMaximum(254)
        self.spinBoxContrast.setProperty("value", 127)
        self.spinBoxContrast.setObjectName("spinBoxContrast")
        self.horizontalLayout_2.addWidget(self.spinBoxContrast)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButtonOK = QtWidgets.QPushButton(DialogBrightnessAndContrastAdjust)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonOK.setIcon(icon)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout_3.addWidget(self.pushButtonOK)
        self.pushButtonReset = QtWidgets.QPushButton(DialogBrightnessAndContrastAdjust)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("resources/reset.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonReset.setIcon(icon1)
        self.pushButtonReset.setObjectName("pushButtonReset")
        self.horizontalLayout_3.addWidget(self.pushButtonReset)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout)

        self.retranslateUi(DialogBrightnessAndContrastAdjust)
        self.horizontalSliderBrightness.valueChanged['int'].connect(self.spinBoxBrightness.setValue)
        self.horizontalSliderContrast.valueChanged['int'].connect(self.spinBoxContrast.setValue)
        self.spinBoxBrightness.valueChanged['int'].connect(self.horizontalSliderBrightness.setValue)
        self.spinBoxContrast.valueChanged['int'].connect(self.horizontalSliderContrast.setValue)
        QtCore.QMetaObject.connectSlotsByName(DialogBrightnessAndContrastAdjust)

    def retranslateUi(self, DialogBrightnessAndContrastAdjust):
        _translate = QtCore.QCoreApplication.translate
        DialogBrightnessAndContrastAdjust.setWindowTitle(_translate("DialogBrightnessAndContrastAdjust", "图像调整 "))
        self.label.setText(_translate("DialogBrightnessAndContrastAdjust", "亮  度："))
        self.label_2.setText(_translate("DialogBrightnessAndContrastAdjust", "对比度: "))
        self.pushButtonOK.setText(_translate("DialogBrightnessAndContrastAdjust", "确定"))
        self.pushButtonReset.setText(_translate("DialogBrightnessAndContrastAdjust", "重置"))
