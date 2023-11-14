# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui
import os

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class AppleBsLinkWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(AppleBsLinkWindow, self).__init__(parent)
        self.setMinimumWidth(300)
        self.setWindowTitle(u'ƻ����������BS���ӹ���')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.nameSpace = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_ctl_path = QtWidgets.QPushButton(u'��')
        self.but_run = QtWidgets.QPushButton(u'����BS')
        self.but_run.setEnabled(False)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.but_ctl_path)
        main_layout.addWidget(self.but_run)

    def create_connections(self):
        self.but_ctl_path.clicked.connect(self.import_ctlFlie)
        self.but_run.clicked.connect(self.link_BS)

    def import_ctlFlie(self):
        path = os.path.dirname(mc.file(exn=True, q=True)) + '/'
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'ѡ��������ļ�', path, '(*.mb *.ma)')
        if file_path[0]:
            mc.file(file_path[0], i=1)
            self.but_ctl_path.setText(file_path[0])
            self.but_run.setEnabled(True)
            self.nameSpace = file_path[0].split('.')[0].split('/')[-1]
        else:
            mc.warning('û��ѡ����Ч����')

    def del_nameSpase(self):
        if not mc.objExists('UI_Connect_Bs_SDK'):
            if self.nameSpace:
                mc.namespace(rm=self.nameSpace, mnr=True, f=True)
            else:
                nsLs = mc.namespaceInfo(lon=True)  #���пռ���
                defaultNs = ["UI", "shared", "mod"]  #Ĭ�Ͽռ���
                pool = [item for item in nsLs if item not in defaultNs]  #��Ĭ�Ͽռ���
                mc.namespace(rm=pool, mnr=1, f=1)  #ɾ���ռ���

    def get_bs(self):
        sel = mc.ls(sl=True)
        bsNode = None
        if sel and mc.nodeType(mc.listRelatives(sel[0], s=True)[0]) == 'mesh':
            allInputs = mc.listHistory(sel[0], interestLevel=True, pruneDagObjects=True)
            if allInputs != None:
                for i in allInputs:
                    if (mc.nodeType(i) == 'blendShape'):
                        bsNode = i
        else:
            mc.warning('ѡ�������Ч��')
            return None

        if bsNode:
            bs_lis = mc.listAttr(bsNode + '.w', m=True)
        else:
            mc.warning('{}����û��bs�ڵ㡣'.format(sel[0]))
            return None

        return bs_lis, bsNode

    def targetGrpList(self):
        tag_lis = ['eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft', 'eyeSquintLeft',
                   'eyeWideLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight', 'eyeLookOutRight', 'eyeLookUpRight',
                   'eyeSquintRight', 'eyeWideRight', 'browOuterUpRight', 'browDownLeft', 'browOuterUpLeft', 'browDownRight',
                   'browInnerUp', 'noseSneerLeft', 'noseSneerRight', 'cheekPuff', 'cheekSquintLeft', 'cheekSquintRight',
                   'mouthClose', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight', 'mouthSmileLeft', 'mouthSmileRight',
                   'mouthFrownLeft', 'mouthFrownRight', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthStretchLeft',
                   'mouthStretchRight', 'mouthRollLower', 'mouthRollUpper', 'mouthPressRight', 'mouthPressLeft',
                   'mouthShrugLower', 'mouthShrugUpper', 'mouthLowerDownLeft', 'mouthLowerDownRight',
                   'mouthUpperUpLeft', 'mouthUpperUpRight', 'jawForward', 'jawRight', 'jawLeft', 'jawOpen',
                   'tongueOut']
        return tag_lis

    def link_BS(self):
        self.del_nameSpase()
        tag_lis = self.targetGrpList()#�������ϵ������б�
        if self.get_bs():#bs�ڵ��ϵ������б�bs�ڵ���
            bs_lis, bs_node = self.get_bs()
            for attrName in tag_lis:
                if attrName in bs_lis:
                    mc.connectAttr('UI_Connect_Bs_SDK.{}'.format(attrName), '%s.%s' % (bs_node, attrName), f=True)
                else:
                    pass
                    #mc.warning('{}��{}��û�ж�Ӧbs�ӿڡ�'.format(attrName, bs_node))


if __name__ == '__main__':
    try:
        my_linkWindow.close()
        my_linkWindow.deleteLater()
    except:
        pass
    finally:
        my_linkWindow = AppleBsLinkWindow()
        my_linkWindow.show()