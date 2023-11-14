# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

nodeName = 'meshToSphere'  #�ڵ�������Ҳ�ǽڵ������ļ����ǲ��������
nodeId = om.MTypeId(0x00004)  #���� Maya �������ͱ�ʶ����


class WoDongNode(ompx.MPxNode):
    @classmethod
    def creatorNode(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def nodeInitialize(cls):
        """
        ��ʼ���ڵ�
        :return:
        """
        pass

    def __init__(self):
        super(WoDongNode, self).__init__()

    def compute(self, plug, dataBlok):
        pass

    def doIt(self, args):
        pass

    def redoIt(self):
        pass

    def undoIt(self):
        """
        ���������Ա�����ʱ��ʹ�ó�������øú���
        :return:
        """
        self.fn_mesh.setPoints(self.initial, om.MSpace.kWorld)

    def isUndoable(self):
        """
        Ĭ�Ϸ���false��������Ϊfalse��ʾdoIt�еĲ������ɳ��������к��������٣�����true��ᱣ���������������������ڳ���ʱ����undoIt
        ����doIt����������øú������жϸò����Ƿ�Ϊ�ɳ���
        :return: True
        """
        return True


def initializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject, 'woDong', '0.1', 'Any')  #mobject,�����Ӧ�̣��汾��������õ�api�汾��anyΪ���У�
    try:
        plugin.registerNode(nodeName, nodeId, WoDongNode.creatorNode, WoDongNode.nodeInitialize,
                            ompx.MPxNode.kDependNode)  #�ڵ����������ڵ�id��������������ʼ������
        om.MGlobal.displayInfo('���سɹ���')
    except Exception as e:
        om.MGlobal.displayError('���ط�������{}��'.format(e))


def uninitializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject)
    try:
        plugin.deregisterNode(nodeId)
        om.MGlobal.displayInfo('ȡ�����سɹ���')
    except Exception as e:
        om.MGlobal.displayError('ȡ�����ط�������{}��'.format(e))
