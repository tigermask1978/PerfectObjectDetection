import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


''' 
    自定义标注矩形框默认外观设置
'''
# 边框颜色和宽度
CUSTOM_RECT_COLOR = Qt.red
CUSTOM_RECT_WIDTH = 8
# 填充
CUSTOM_RECT_BRUSH = QBrush(Qt.transparent)
# 层次
CUSTOM_RECT_Z_VALUE = 2
# 选中时的外观
CUSTOM_RECT_SELECTED_COLOR = Qt.green
CUSTOM_RECT_SELECTED_WIDTH = 8

'''
    自定义ImageView设置
'''
# 背景
CUSTOM_IMAGEVIEW_BG_BRUSH = QBrush(Qt.black)
# 图像缩放比例
CUSTOM_ZOOM_IN_FACTOR = 1.25   #放大
CUSTOM_ZOOM_OUT_FACTOR = 0.8   #缩小


class BoltAnnoRect(QGraphicsRectItem):
    def __init__(self,x,y,width,height,parent=None):
        '''
            自定义标注矩形框
            构造函数：
                customRectItem = BoltAnnoRect(1830,1740,80,100)
        '''
        super(QGraphicsRectItem,self).__init__(x,y,width,height,parent)

        # 标识
        self.id = None

        # 默认外观设置
        pen = QPen(CUSTOM_RECT_COLOR)
        pen.setWidth(CUSTOM_RECT_WIDTH)

        self.setPen(pen)    
        self.setBrush(CUSTOM_RECT_BRUSH)
        self.setZValue(CUSTOM_RECT_Z_VALUE)

        # 事件处理
        # 可选择
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        # 可聚焦
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)


    def mouseReleaseEvent(self, e):        
        # pen = QPen(CUSTOM_RECT_SELECTED_COLOR)        
        # self.setPen(pen)
        self.setSelectedState()
        QGraphicsRectItem.mouseReleaseEvent(self,e)

    def setSelectedState(self):
        pen = QPen(CUSTOM_RECT_SELECTED_COLOR)   
        pen.setWidth(CUSTOM_RECT_SELECTED_WIDTH)     
        self.setPen(pen)

    def restorDefaultState(self):
        pen = QPen(CUSTOM_RECT_COLOR)
        pen.setWidth(CUSTOM_RECT_WIDTH)
        self.setPen(pen)


class ImageView(QGraphicsView):
    '''
        支持缩放的QGraphicsView
    '''
    # 自定义信号，用于发送选中某标注的信号
    annoRectSelected = pyqtSignal(int)
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)      

        # 缩放参数
        self._zoom = 0
        # 加载的图像文件
        self.picFile = None        
        # 图像文件通过QPixmap存储,传入QGraphicsScene
        # 加载图像的QGraphicsPixmapItem
        self.pixmapItem = QGraphicsPixmapItem()        
        # QGraphicsScene中存储所有信息，图像和标注
        self.scene = QGraphicsScene()
        self.scene.addItem(self.pixmapItem)
        # 与QGraphicsView建立关联，在UI中显示
        self.setScene(self.scene)

        # 标注结果(字典列表)
        self.annoRects = []
        # 当前标注
        self.selectedRectId = None

        # 去除滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        # 缩放方式
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFrameShape(QFrame.NoFrame)

        #默认背景色 
        self.setBackgroundBrush(CUSTOM_IMAGEVIEW_BG_BRUSH)
        
        # 事件
        QMetaObject.connectSlotsByName(self)
        # self.scene.selectionChanged.connect(self.onSceneSelectionChanged)
        self.scene.focusItemChanged.connect(self.onSceneFocusItemChanged)

    

    def fitInView(self, scale=True):
        # 重写QGraphicsView的fitInView方法
        rect = QRectF(self.pixmapItem.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.picFile is not None:
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                                viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def keyReleaseEvent(self,event):
        # 键盘操作缩放
        if self.picFile is not None:
            keyId = event.key()
            if keyId == 61:  # '+'
                factor = CUSTOM_ZOOM_IN_FACTOR
                self._zoom += 1
            elif keyId == 45:  # '-'
                factor = CUSTOM_ZOOM_OUT_FACTOR
                self._zoom -= 1
            
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def wheelEvent(self,event):    
        if self.picFile is not None:
            if event.angleDelta().y() > 0:
                factor = CUSTOM_ZOOM_IN_FACTOR
                self._zoom += 1
            else:
                factor = CUSTOM_ZOOM_OUT_FACTOR
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0
        
    def onSceneSelectionChanged(self):
        for item in self.scene.selectedItems():
            print(item.__class__)
    
    def onSceneFocusItemChanged(self, newFocusItem, oldFocusItem, reason):
        print(type(newFocusItem).__name__)
        print(type(oldFocusItem).__name__)
        print(self.annoRects)      

        if (type(newFocusItem).__name__) == 'BoltAnnoRect':
            self.selectedRectId = newFocusItem.id
            # 发送信号，在主界面中，主界面响应后，在列表中选中对应item
            self.annoRectSelected.emit(newFocusItem.id)

        if (newFocusItem is not None) and (oldFocusItem is None):
            for item in self.scene.items():
                if (type(item).__name__) == 'BoltAnnoRect':
                    item.restorDefaultState()
            newFocusItem.setSelectedState()
        if (newFocusItem is not None) and (oldFocusItem is not None):
            oldFocusItem.restorDefaultState()
            newFocusItem.setSelectedState()
        if (newFocusItem is None) and (oldFocusItem is not None):
            pass    
        print(self.selectedRectId)
        print(self.getLabelById(self.selectedRectId))
        
    def resizeEvent(self, event):                
        self.fitInView()    
        
    def clearAnnoRects(self):
        '''
            清除所有标注
        '''
        for item in self.scene.items():
            if type(item).__name__ == 'BoltAnnoRect':
                self.scene.removeItem(item)

    def getLabelById(self, id):
        res = None
        if len(self.annoRects) > 0 :
            for item in self.annoRects:
                if item.get('id') == id:
                    res = item.get('className')
        return res

    def loadPicFile(self,picFile):
        '''
            加载图像
        '''
        picName = picFile
        pic = QPixmap(picName)
        self.picFile = picName       
        self.pixmapItem.setPixmap(pic)

    def loadAnnoRects(self, annoRects):
        '''
            加载标注
        '''        
        self.annoRects = []
        self.clearAnnoRects()
        
        for anno in annoRects:
            id = anno['id']
            label = anno['className']
            shape = anno['shape']
            xmin = shape[0]
            ymin = shape[1]
            w = shape[2] - shape[0]
            h = shape[3] - shape[1]
            customRectItem = BoltAnnoRect(xmin, ymin, w, h)
            customRectItem.id = id
            self.annoRects.append({
                'id' : id,
                'className' : label
            })
            self.scene.addItem(customRectItem)       
            
    def selectAnnoRectById(self, id):
        '''
            选择某一个标注
        '''
        for item in self.scene.items():
            if type(item).__name__ == 'BoltAnnoRect':
                if item.id == id:
                    item.setSelectedState()
                else:
                    item.restorDefaultState()
               
        

