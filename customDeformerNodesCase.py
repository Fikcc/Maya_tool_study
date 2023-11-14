# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import math

nodeName = 'meshToSphere'  #�ڵ�������Ҳ�ǽڵ������ļ����ǲ��������
nodeId = om.MTypeId(0x00004)  #���� Maya �������ͱ�ʶ����


class WoDongNode(ompx.MPxDeformerNode):
    @classmethod
    def creatorNode(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def nodeInitialize(cls):
        """
        ��ʼ���ڵ�
        :return:
        """
        nAttr = om.MFnNumericAttribute()
        outGeo = ompx.cvar.MPxGeometryFilter_outputGeom

        cls.input = nAttr.create('up', 'up', om.MFnNumericData.kFloat, 0.0)
        nAttr.setStorable(True)
        nAttr.setConnectable(True)
        nAttr.setWritable(True)
        nAttr.setKeyable(True)
        cls.addAttribute(cls.input)
        cls.attributeAffects(cls.input, outGeo)

    def __init__(self):
        super(WoDongNode, self).__init__()

    def deform(self, dataBlok, it, mat, multiIndex):
        """
        ʹ��cmds.deformer(type='meshToSphere')�����ñ�����Ч��
        :param dataBlok:�����ڵ����Դ洢�����ݿ�
        :param it:MItGeometry���ͣ������ڱ���ģ�͵ĵ�
        :param mat:
        :param multiIndex:
        :return:
        """
        up = dataBlok.inputValue(self.input).asFloat()
        en = dataBlok.inputValue(ompx.cvar.MPxGeometryFilter_envelope).asFloat()
        vec = om.MVector(0, up*en, 0)
        while not it.isDone():
            point = it.position()
            it.setPosition(point+vec)
            it.next()

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
                            ompx.MPxNode.kDeformerNode)  #�ڵ����������ڵ�id��������������ʼ������
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
