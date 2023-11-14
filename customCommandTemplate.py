# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import math

cmdName = 'box_num'#�������ƣ��ļ����ǲ��������
numFlag = '-num'
numFlagLong = '-number'

class PrintStringCmd(ompx.MPxCommand):
    @classmethod
    def creatorCmd(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def syntaxCreator(cls):
        """
        �������β���
        :return:
        """
        s = om.MSyntax()
        s.addFlag(numFlag, numFlagLong, om.MSyntax.kDouble)
        s.enableEdit(False)
        s.enableQuery(False)
        return s

    def __init__(self):
        super(PrintStringCmd, self).__init__()


    def doIt(self, args):
        """
        �������е����������￪ʼ
        :param args:
        :return:
        """
        argData = om.MArgDatabase(self.syntax(), args)
        if argData.isFlagSet(numFlag):  #���յ��Ĳ���Ϊ�ñ�־ʱ
            self.val = argData.flagArgumentDouble(numFlag, 0)  #��ȡ�ñ�־�Ĳ����ĵ�һ��ֵ
            self.redoIt()#����ʱ�����������������ʱֱ�ӵ���redoIt����Ҫ��ú�������
        else:
            om.MGlobal.displayError('û��������Чֵ���ڼ��㡣')

    def redoIt(self):
        """
        ��������൱��ctrl-y
        ��Ҫ�������Ӹú������βδ����������������ᱨ����Ϊ��������ʱ������ú�������
        :return:
        """
        #dagMod����ŵ����д����С���������������ʱֱ�������������dagMod�ŵ�init�У�
        # ����ʹ�ó���Ҳֻ�ǽ�dagMod.doIt�Ĳ�������ŵ���ջ����dagMod����������һ�����ݣ���dagMod����������һ������
        # ��������dagMod.doIt�������һ�ε���������һ�ε�����һ���ͷ�
        #����ڸú����У���ÿ�����ж�������ʵ������һ��om.MDagModifier���Ҳ�Ӱ�쳷��
        self.dagMod = om.MDagModifier()
        node = self.dagMod.createNode('joint')
        self.dagMod.doIt()  #���ɽڵ�
        box = om.MFnDependencyNode(node)
        box.setName('box_{}'.format(self.val))  #���ýڵ�����
        plug = box.findPlug('translateY')
        plug.setFloat(self.val)  #���ýڵ�����ֵ

        self.setResult(self.val)  #��# Result:�ķ�ʽ��������Ϣ
        self.displayInfo(self.val)  #������������ʽ�����أ�errorҲ������ִ��
        self.displayError(self.val)
        self.displayWarning(self.val)
        self.setResult(self.className())  #���ظ���������ƣ��̳еĸ�������MPxCommand


    def undoIt(self):
        """
        ���������Ա�����ʱ��ʹ�ó�������øú���
        :return:
        """
        self.dagMod.undoIt()

    def isUndoable(self):
        """
        Ĭ�Ϸ���false��������Ϊfalse��ʾdoIt�еĲ������ɳ��������к��������٣�����true��ᱣ���������������������ڳ���ʱ����undoIt
        ����doIt����������øú������жϸò����Ƿ�Ϊ�ɳ���
        :return: True
        """
        return True



def initializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject, 'woDong', '0.1', 'Any')#mobject,�����Ӧ�̣��汾��������õ�api�汾��anyΪ���У�
    try:
        plugin.registerCommand(cmdName, PrintStringCmd.creatorCmd, PrintStringCmd.syntaxCreator)
        om.MGlobal.displayInfo('���سɹ���')
    except Exception as e:
        om.MGlobal.displayError('���ط�������{}��'.format(e))

def uninitializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject)
    try:
        plugin.deregisterCommand(cmdName)
        om.MGlobal.displayInfo('ȡ�����سɹ���')
    except Exception as e:
        om.MGlobal.displayError('ȡ�����ط�������{}��'.format(e))
