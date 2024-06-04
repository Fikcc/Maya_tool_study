#conding=gbk
from PySide2 import QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as mc

from PySide2 import QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

class MyDockableWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, objname):
        super(MyDockableWindow, self).__init__()        

        self.setWindowTitle('My Dockable Window')
        self.resize(500, 400)
        self.setObjectName(objname)

objname = 'ssa'#���ڵ�objname����ָ�����ÿ���������һ�����Ҵ��ڻ��½��������ܱ�֤����Ψһ
try:
    #���ڴ���Ψһ������Ҫ��ɾ��ԭ�д��ڣ����򱨴�������Ʋ�Ψһ��ɾ��ʱ����objname��'WorkspaceControl'
    mc.deleteUI('{}WorkspaceControl'.format(objname))
except:
    pass
finally:
    my_window = MyDockableWindow(objname)
    my_window.show(dockable=True)