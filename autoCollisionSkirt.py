# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


def maya_main_window():
    return wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)


class AutoCollisionSkirtWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(AutoCollisionSkirtWindow, self).__init__(parent)

        self.setWindowTitle(u'ȹ�Ӱ󶨹���')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lin_name = QtWidgets.QLineEdit()
        self.lin_name.setText('skirt')
        self.spin_jntNum = QtWidgets.QSpinBox()
        self.spin_jntNum.setValue(12)
        self.spin_jntNum.setMinimum(4)
        self.but_appJnt = QtWidgets.QPushButton(u'������ײ�ؽ�->>')
        self.lin_jnts = QtWidgets.QLineEdit()
        self.but_cratCrv = QtWidgets.QPushButton(u'���ɶ�λ����')
        self.but_run = QtWidgets.QPushButton(u'����')

    def create_layout(self):
        layout_row = QtWidgets.QFormLayout()
        layout_row.addRow(u'����:', self.lin_name)
        layout_row.addRow(u'����ײ�ؽ�����:', self.spin_jntNum)

        layout_collisionJnt = QtWidgets.QHBoxLayout()
        layout_collisionJnt.addWidget(self.but_appJnt)
        layout_collisionJnt.addWidget(self.lin_jnts)

        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.addLayout(layout_row)
        layout_main.addLayout(layout_collisionJnt)
        layout_main.addWidget(self.but_cratCrv)
        layout_main.addWidget(self.but_run)
        layout_main.setContentsMargins(3, 3, 3, 3)
        layout_main.setSpacing(2)

    def create_connections(self):
        self.but_appJnt.clicked.connect(self.get_collision_joints)
        self.but_cratCrv.clicked.connect(self.create_curve)
        self.but_run.clicked.connect(self.create_collision_system)

    def get_collision_joints(self):
        """
        ��ȡ���������Ĺؽ�
        :return:
        """
        sel_lis = mc.ls(sl=True)
        if sel_lis and mc.objectType(sel_lis[0]) == 'joint' and mc.listRelatives(sel_lis[0]):
            self.lin_jnts.setText(sel_lis[0])
        else:
            om.MGlobal.displayError('ѡ�����ײ�ؽڶ��󲻺��ʡ�Ӧ��ѡ��һ���ؽڣ��Ҹùؽ���һ���Ӽ�����')

    def create_curve(self):
        """
        �������ڶ���ȹ�����µ����ߣ����ߵ�ep�㼴���ɵ���Ƥ�ؽ�������λ��
        :return:
        """
        if not self.lin_name.text():
            mc.error('û��ָ����ײϵͳ���ơ�')
        if not self.lin_jnts.text() and not mc.objExists(self.lin_jnts.text()):
            mc.error('û��ָ����ײ�ؽڻ���ָ���Ķ�����Ч��')
        self.colJnt_rot = self.lin_jnts.text()
        self.colJnt_end = mc.listRelatives(self.colJnt_rot)[0]
        self.col_name = self.lin_name.text()
        jnt_num = self.spin_jntNum.value()

        jnt_rot_pos = mc.xform(self.colJnt_rot, q=True, t=True, ws=True)
        jnt_end_pos = mc.xform(self.colJnt_end, q=True, t=True, ws=True)
        normal_aix = mc.xform(self.colJnt_end, q=True, t=True, os=True)#�������ؽڵ��Ӽ��������Ϸ������·�ʱ���ڶ�λ���ߵĳ���

        self.crv_up = mc.circle(c=jnt_rot_pos, r=1, s=jnt_num, nr=normal_aix)[0]
        self.crv_down = mc.circle(c=jnt_end_pos, r=2, s=jnt_num, nr=normal_aix)[0]

    def create_collision_system(self):
        #����һ���ܵ���
        self.root_grp = mc.group(n='grp_collision_001', em=True, w=True)
        #����ȹ���ϵ���Ƥ�ؽ�
        skinJnt_lis, ctrlGrp_lis = self.create_joints()
        #���������ϵĶ�λ������Ƥ�ؽڴ��Ķ�λ����
        loc_hand, loc_crv, loc_aim, dis_lis = self.create_locInfo(skinJnt_lis)
        #�������ڼ���Ƕȵ���عؽ���ik��Ŀ��Լ����
        jnt_rot = self.create_aimInfo(loc_hand, loc_crv, loc_aim)
        #���ɼ��㴥����صĽڵ�
        self.create_nodeInfo(loc_aim, jnt_rot, dis_lis, skinJnt_lis, ctrlGrp_lis)

    def create_joints(self):
        """
        �����������������϶�Ӧ��ep��λ�����ɹؽڣ������ɿ��������Ӧ�����飬������������ĳ��ָ�������ؽ�
        :return:��Ƥ�ؽ����б�������������ƫ�Ƹ�����
        """
        jnt_lis = []
        conn_lis = []
        grp_jnt = mc.group(n='grp_{}_skinJnt_001'.format(self.col_name), w=True, em=True)
        grp_ctrl = mc.group(n='grp_{}_ctl_001'.format(self.col_name), w=True, em=True)
        for i in range(mc.ls('{}.ep[*]'.format(self.crv_up), fl=True).__len__()):
            jnt_up = mc.createNode('joint', n='jnt_{}_{:03d}'.format(self.col_name, i + 1))
            jnt_down = mc.createNode('joint', n='{}_end_{:03d}'.format(jnt_up.rsplit('_', 1)[0], i + 1))
            ctrl = mc.circle(n='ctl_{}_{:03d}'.format(self.col_name, i + 1), nr=[1, 0, 0], r=0.5)[0]
            mm.eval('DeleteHistory;')
            grp_offset = mc.group(n='offset_{}_{:03d}'.format(self.col_name, i + 1), w=True)
            grp = mc.group(n='grp_{}_{:03d}'.format(self.col_name, i + 1), w=True)
            mc.parentConstraint(ctrl, jnt_up, mo=False)

            up_ep_pos = mc.xform('{}.ep[{}]'.format(self.crv_up, i), q=True, ws=True, t=True)
            down_ep_pos = mc.xform('{}.ep[{}]'.format(self.crv_down, i), q=True, ws=True, t=True)
            mc.xform(grp, t=up_ep_pos, ws=True)
            mc.xform(jnt_down, t=down_ep_pos, ws=True)

            link = mc.aimConstraint(jnt_down, grp, o=(0, 0, 0), aim=(1, 0, 0), u=(0, 1, 0), wut='object',
                                    mo=False, wuo=self.colJnt_rot)
            mc.xform(jnt_down, ro=mc.xform(grp, q=True, ro=True, ws=True), ws=True)

            mc.delete(link)
            mc.makeIdentity(jnt_down, a=True, r=True, n=False, pn=True)
            mc.parent(jnt_down, jnt_up)
            mc.parent(jnt_up, grp_jnt)
            mc.parent(grp, grp_ctrl)

            jnt_lis.append(jnt_up)
            conn_lis.append(grp_offset)
        mc.parent(grp_jnt, grp_ctrl, self.root_grp)
        return jnt_lis, conn_lis

    def create_locInfo(self, skin_jnts):
        """
        ����Ƥ�ؽڴ����ö�λ��
        �������ؽ��Ӽ����������ڶ�λ��תik����Ķ�λ��������ik�ֱ��Ķ�λ��
        :param skin_jnts:��Ƥ�ؽ����б�
        :return:����ik�ֱ��Ķ�λ�����������ϵ����ڲ��Ķ�λ��������λik�������Ķ�λ���������ڵ��shape��
        """
        grp_other = mc.group(n='grp_{}_other_001'.format(self.col_name), p=self.root_grp, em=True)
        grp_dis = mc.group(n='grp_{}_dis_001'.format(self.col_name), p=self.root_grp, em=True)

        loc_hand = mc.spaceLocator(n='loc_{}_hand'.format(self.col_name))[0]
        loc_crv = mc.spaceLocator(n='loc_{}_crv'.format(self.col_name))[0]
        loc_aim = mc.spaceLocator(n='loc_{}_aim'.format(self.col_name))[0]
        pntOnCvr = mc.createNode('nearestPointOnCurve', n='pntOnCrv_{}_001'.format(self.col_name))

        mc.connectAttr('{}.worldSpace[0]'.format(mc.listRelatives(self.crv_down, s=True)[0]),
                       '{}.inputCurve'.format(pntOnCvr))
        mc.connectAttr('{}.worldPosition[0]'.format(mc.listRelatives(loc_hand, s=True)[0]),
                       '{}.inPosition'.format(pntOnCvr))
        mc.connectAttr('{}.position'.format(pntOnCvr), '{}.translate'.format(loc_crv))

        mc.xform(loc_hand, t=mc.xform(self.colJnt_end, ws=True, t=True, q=True), ws=True)
        mc.parent(loc_hand, loc_crv, loc_aim, grp_other)
        mc.parentConstraint(self.colJnt_end, loc_hand, mo=False)
        mc.xform(loc_aim, t=mc.xform(self.colJnt_end, ws=True, t=True, q=True), ws=True)
        if mc.listRelatives(self.colJnt_rot, p=True):
            mc.parentConstraint(mc.listRelatives(self.colJnt_rot, p=True)[0], loc_aim, mo=False)

        dis_lis = []
        for jnt in skin_jnts:
            loc = mc.spaceLocator(n='{}'.format(jnt.replace('jnt', 'loc')))[0]
            dis = mc.createNode('distanceDimShape', n='{}Shape'.format(jnt.replace('jnt', 'dis')))
            dis_lis.append(dis)

            mc.xform(loc, ws=True, t=mc.xform(jnt, ws=True, t=True, q=True))
            mc.parent(loc, mc.listRelatives(dis, p=True)[0], grp_dis)
            mc.connectAttr('{}.worldPosition[0]'.format(loc), '{}.startPoint'.format(dis))
            mc.connectAttr('{}.worldPosition[0]'.format(loc_crv), '{}.endPoint'.format(dis))

        return loc_hand, loc_crv, loc_aim, dis_lis

    def create_aimInfo(self, loc_hand, loc_crv, loc_aim):
        """
        ͨ�������ؽ�����hand��λ������������������λ�ã�Ȼ��ʹ��Ŀ��Լ�����ؽڶ�׼�����϶�λ��������Ŀ��Լ���ؽ���ָ��ؽڼ�ľ���
        Ϊ����ʱΪδ��������û����ײ����������Ϊ�������������ڳ�����Ӧ��Ƥ�ؽڵ���ת
        :param loc_hand: �����ؽ������Ķ�λ��
        :param loc_crv: �����ϵĶ�λ��
        :param loc_aim: �����ؽ��Ӽ�λ�õĶ�λ��
        :return:Ŀ��Լ�������ڼ�����ת�ǶȵĹؽ�
        """
        mc.select(cl=True)
        jnt_aim = mc.joint(n='jnt_{}_aim_001'.format(self.col_name),
                           p=mc.xform(self.colJnt_rot, q=True, ws=True, t=True))#ik���ؽ�
        jnt_aim_end = mc.joint(n='jnt_{}_aim_end_001'.format(self.col_name),
                               p=mc.xform(loc_crv, q=True, ws=True, t=True))#ik�ӹؽڣ��ؽ�λ�������߶�λ����
        mc.select(cl=True)
        jnt_rot = mc.joint(n='jnt_{}_rot_001'.format(self.col_name),
                           p=mc.xform(self.colJnt_rot, q=True, ws=True, t=True))#��ת���ؽ�
        mc.joint(n='jnt_{}_rot_end_001'.format(self.col_name), p=mc.xform(self.colJnt_end, q=True, ws=True, t=True))#��ת�ӹؽ�
        mc.parent(jnt_rot, jnt_aim)
        mc.joint(jnt_aim, e=True, oj='xyz', sao='yup', ch=True, zso=True)#��ik���ؽ����ؽڶ���ʹz�ᳯ���Ӽ�

        #����ik�ӹؽ�Ϊik�ؽڵĵ�һ�������壬����ik�ؽ���ָ���ӹؽ�
        # ��ת�ؽ���ik�ؽڳ���һ����תֵ������ʹ�õ��ǹؽڶ���������תֵ������jointOrient�У������ó������任�����ڼ���
        rot = mc.getAttr('{}.jointOrientZ'.format(jnt_rot))
        mc.setAttr('{}.jointOrientZ'.format(jnt_rot), 0)
        mc.setAttr('{}.rotateZ'.format(jnt_rot), rot)

        #�����ؽ�Լ���Ķ�λ������ת�ؽ���Ŀ��Լ����ʹ�ö�����תָ�����Ϸ���ʹ��ת�ؽڵ�������ik�ؽڵ�����һ�£����ⷽ��һ�µ�����ת��ֵ�����ڶ����
        mc.aimConstraint(loc_hand, jnt_rot, o=(0, 0, 0), aim=(1, 0, 0), u=(0, 0, 1), wut='objectrotation', wu=(0, 0, 1),
                         wuo=jnt_aim)
        #��ik�ؽ���ikRPsolver,ֻ��ʹ���������ik����ΪikSCsolver�޷���������Լ������������Ҫʹ��תֻ������һ������
        aim_hadl = mc.ikHandle(sj=jnt_aim, ee=jnt_aim_end, sol='ikRPsolver')[0]
        mc.parent(aim_hadl, loc_crv)
        mc.setAttr('{}.v'.format(aim_hadl), 0)
        #��ik��������Լ����������ܻ���ֽ�y����z�ᵱ�����������򣬺����д������ж�
        mc.poleVectorConstraint(loc_aim, aim_hadl)

        grp_jnt = mc.group(n='grp_{}_jnt_001'.format(self.col_name), p=self.root_grp, em=True)
        mc.parent(jnt_aim, grp_jnt)
        mc.setAttr('{}.v'.format(grp_jnt), 0)

        return jnt_rot

    def create_nodeInfo(self, loc_aim, jnt_rot, dis_lis, jnt_lis, grp_lis):
        """
        ���������߼��Ͳ���Ӱ��
        :param loc_aim: �����ؽ���
        :param jnt_rot:��ת�ؽ���
        :param dis_lis:���ڵ��б�
        :param jnt_lis:��Ƥ�ؽ��б�
        :param grp_lis:������������ƫ����
        :return:
        """
        mc.addAttr(loc_aim, ln='offset', at='double', min=0, dv=0, k=True)#���ƫ�����ԣ����ڿ�����ײ����
        mc.addAttr(loc_aim, ln='range', at='double', min=0, max=1, dv=0.2, k=True)#��ӷ�Χ���ԣ�����������Χ����
        rvs_range = mc.createNode('reverse', n='rvs_{}_range_001'.format(self.col_name))#���ڽ�������Χ���Ե�ֵ���򣬷����˵Ĺ���˼ά
        add_offset = mc.createNode('addDoubleLinear', n='add_{}_offset_001'.format(self.col_name))#���ڽ���ײ������ƫ��������ӣ�����������ײ����
        clp_offset = mc.createNode('clamp', n='clp_{}_offset_001'.format(self.col_name))#����������ײ���룬����Ƥ�ؽ���תֻ����0��180��֮��
        mc.setAttr('{}.maxR'.format(clp_offset), 180)

        mc.connectAttr(loc_aim + '.offset', add_offset + '.input1')
        mc.connectAttr(add_offset + '.output', clp_offset + '.inputR')
        mc.connectAttr(loc_aim + '.range', rvs_range + '.inputX')

        mult = 1
        aix_dir = {1: 'X', 2: 'Y', 3: 'Z'}
        mult_ratio = mc.createNode('multiplyDivide', n='mult_{}_ratio_001'.format(self.col_name))#���ɵ�һ�����ڼ�����̾����뵱ǰ��������Ľڵ�
        mult_itplat = mc.createNode('multiplyDivide', n='mult_{}_itplat_001'.format(self.col_name))#���ɴ�����ת�ĳ˳��ڵ㣬ֻ�е���ת�ؽ������תֵΪ��ֵʱ�Ż��д���1��ֵ���
        mult_rot = mc.createNode('multiplyDivide', n='mult_{}_rotate_001'.format(self.col_name))#������ת����ڵ㣬����תֵ�������ʹ��Ƥ�ؽ�������ת
        for dis, jnt, grp in zip(dis_lis, jnt_lis, grp_lis):
            suffix = dis.rsplit('_', 1)[1].replace('Shape', '')
            if mult == 4:#Ϊ��ʡ�ڵ㣬���˳��������һ���ڵ��ڣ�����ʹ����ʱ�����µĽڵ����ڼ���
                mult = 1
                mult_ratio = mc.createNode('multiplyDivide', n='mult_{}_ratio_{}'.format(self.col_name, suffix))
                mult_itplat = mc.createNode('multiplyDivide', n='mult_{}_itplat_{}'.format(self.col_name, suffix))
                mult_rot = mc.createNode('multiplyDivide', n='mult_{}_rotate_{}'.format(self.col_name, suffix))

            #д�������Ƥ�ؽ������ȹ�������ϵ�λ�þ��룬�õ��Ǿ����Ӧ��ת�ؽ�����ĵ�
            # ����ʹ�����������϶�Ӧ��ep�㣬�����°�����Ϊ��Բʱ���ܳ��ֶ�Ӧep�㲻�Ǿ�����ת�ؽ�����ĵ�
            mc.setAttr('{}.input1{}'.format(mult_ratio, aix_dir[mult]), self.get_distance(jnt))
            mc.setAttr('{}.operation'.format(mult_ratio), 2)
            mc.connectAttr('{}.distance'.format(dis), '{}.input2{}'.format(mult_ratio, aix_dir[mult]))

            #����ӳ��ڵ㣬����Χ�������ӵ�inputMin���Կ���������ת������
            rmap_nod = mc.createNode('remapValue', n='rmap_{}_range_{}'.format(self.col_name, suffix))
            mc.connectAttr('{}.output{}'.format(mult_ratio, aix_dir[mult]), '{}.inputValue'.format(rmap_nod))
            mc.connectAttr(rvs_range + '.outputX', '{}.inputMin'.format(rmap_nod))

            mc.connectAttr('{}.outValue'.format(rmap_nod), '{}.input1{}'.format(mult_itplat, aix_dir[mult]))
            mc.connectAttr('{}.outputR'.format(clp_offset), '{}.input2{}'.format(mult_itplat, aix_dir[mult]))

            if mc.getAttr(jnt_rot+'.rotateY'):#��Ϊ�������ʱ����ת�ؽڵ���תֵ��y����
                if not mc.listConnections('jnt_skirt_rot_001.rotateY', s=0, scn=1):
                    mc.connectAttr(jnt_rot + '.rotateY', add_offset + '.input2')

                mc.connectAttr('{}.output{}'.format(mult_itplat, aix_dir[mult]),
                               '{}.input1{}'.format(mult_rot, aix_dir[mult]))
                mc.connectAttr('{}.output{}'.format(mult_rot, aix_dir[mult]), '{}.rotateZ'.format(grp))
                mc.setAttr('{}.input2{}'.format(mult_rot, aix_dir[mult]), -1)
            else:#����ʱ��תֵ��z����ʱ
                mc.delete(mult_rot)
                if not mc.listConnections('jnt_skirt_rot_001.rotateZ', s=0, scn=1):
                    mc.connectAttr(jnt_rot + '.rotateZ', add_offset + '.input2')
                mc.connectAttr('{}.output{}'.format(mult_itplat, aix_dir[mult]), '{}.rotateZ'.format(grp))

            mult += 1

    def get_distance(self, jnt):
        """
        ͨ��distanceBetween�ڵ��ȡ��Ƥ�ؽ����°�����������ĵ㵽��Ƥ�ؽڵ���̾���
        :param jnt: Ҫ�������Ƥ�ؽ�
        :return: ��̾����ֵ
        """
        dis = mc.createNode('distanceBetween')
        npc = mc.createNode('nearestPointOnCurve')

        jnt_pos = mc.xform(jnt, q=True, ws=True, t=True)
        [mc.setAttr(npc + '.inPosition{}'.format(aix), v) for aix, v in zip(['X', 'Y', 'Z'], jnt_pos)]
        [mc.setAttr(dis + '.point1{}'.format(aix), v) for aix, v in zip(['X', 'Y', 'Z'], jnt_pos)]
        mc.connectAttr(mc.listRelatives(self.crv_down, s=True)[0]+'.worldSpace[0]', npc+'.inputCurve')
        [mc.setAttr(dis + '.point2{}'.format(aix), v) for aix, v in zip(['X', 'Y', 'Z'], mc.getAttr(npc+'.position')[0])]
        val = mc.getAttr(dis+'.distance')
        mc.delete(dis, npc)

        return val




if __name__ == '__main__':
    try:
        skirt_window.close()
        skirt_window.deleteLater()
    except:
        pass
    finally:
        skirt_window = AutoCollisionSkirtWindow()
        skirt_window.show()
