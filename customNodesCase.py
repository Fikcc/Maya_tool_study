# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import math

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
        nAttr = om.MFnNumericAttribute()
        cls.output = nAttr.create('output', 'out', om.MFnNumericData.kDoubleArray, 0.0)  #���Գ�����������ֵ���͡�Ĭ��ֵ
        nAttr.setStorable(False)#�ɴ���
        #nAttr.setWritable(False)#��д
        cls.addAttribute(cls.output)

        cls.input = nAttr.create('input', 'in', om.MFnNumericData.kDoubleArray, 0.0)  #���Գ�����������ֵ���͡�Ĭ��ֵ
        nAttr.setStorable(True)  #�ɴ���
        nAttr.setConnectable(True)  #������
        nAttr.setWritable(True)  #��д
        nAttr.setKeyable(True)#��k֡
        cls.addAttribute(cls.input)

        #���������Է����仯ʱ��ֻ����ָ����������ԡ�������Բ��ܱ�����Ϊ��k֡������÷���ʧЧ��
        # ����ڵ��ʼ��û��ʹ�ø÷������򲻻����compute����,�����������Է����ı䲻��ˢ��compute
        cls.attributeAffects(cls.input, cls.output)

    def __init__(self):
        super(WoDongNode, self).__init__()

    def compute(self, plug, dataBlok):
        """
        ���ݽڵ��������¼�����������plug������Ҫ���¼��������ֵ��dataBlok����ڵ��������ԵĴ洢��
        :param plug:��Ҫ���¼��������
        :param dataBlok:�����ڵ����Դ洢�����ݿ�
        :return:kSuccess����ɹ�;kFailure����ʧ��
        """
        if plug == self.output:
            inputValue = dataBlok.inputValue(self.input).asFloat()
            outHandle = dataBlok.outputValue(self.output)

            result = math.sin(inputValue)

            outHandle.setFloat(result)

            dataBlok.setClean(plug)
            return True
        else:
            return om.kUnknownParameter


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
