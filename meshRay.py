# coding=gbk
import maya.OpenMaya as om
import maya.cmds as mc

import sys
import os


def caller_info():
    """
    �˺��������йص��÷����ļ�·�����кŵ���Ϣ��
    Returns:
    back_path (str): ���÷����ļ�·����
    back_lin (int): ���÷��ļ��е��кš�
    """
    back_frame = sys._getframe().f_back.f_back
    back_path = back_frame.f_code.co_filename
    back_file = os.path.basename(back_path)
    back_lin = back_frame.f_lineno

    return back_path, back_lin


def feedback(txt, info=False, warning=False, error=False, time=3000, block=True):
    """
    �����ṩ��������ʾ������Ϣ��
    Parameters:
    txt (str): Ҫ��ʾ����Ϣ��
    info (bool): ���Ϊ True������ʾΪ��ͨ��Ϣ��
    warning (bool): ���Ϊ True������ʾΪ������Ϣ��
    error (bool): ���Ϊ True������ʾΪ������Ϣ��
    time (int): ��ʾ��Ϣ��ʱ�䣨�Ժ���Ϊ��λ����
    block (bool): ���Ϊ True����������ʱ��ϳ���

    Returns:
    None
    """
    path, line = caller_info()
    txt = '�ļ�{}��{}��:{}'.format(path, line, txt)

    if not info and not warning and not error:
        info = True
    if info:
        mc.inViewMessage(amg='<div style="text-align: center;"></div><font color="lightcyan">{}</font>'.format(txt),
                         pos='midCenterBot', f=True, fst=time)
        om.MGlobal.displayInfo('{}'.format(txt))
    elif warning:
        mc.inViewMessage(amg='<div style="text-align: center;"></div><font color="yellow">{}</font>'.format(txt),
                         pos='midCenterBot', f=True, fst=time)
        om.MGlobal.displayWarning('{}'.format(txt))
    elif error:
        mc.inViewMessage(amg='<div style="text-align: center;"></div><font color="red">{}</font>'.format(txt),
                         pos='midCenterBot', f=True, fst=time)
        if block:
            raise RuntimeError(txt)
        else:
            om.MGlobal.displayError(txt)


class MeshRay(object):
    @classmethod
    def is_float_lis(cls, lis):
        """
        ���Ƕ���б��е�����Ԫ���Ƿ��Ǹ�������������
        Args:
        lis (list): Ҫ����Ƕ���б�
        Returns:
        bool: �������Ԫ�ض��Ǹ���������������Ϊ True������Ϊ False��
        """
        for inf in lis:
            if isinstance(inf, list) or isinstance(inf, tuple):
                cls.is_float_lis(inf)
            elif not isinstance(inf, float) and not isinstance(inf, int):
                feedback('����{}�������б������'.format(inf), error=True)
                return False
        return True

    @classmethod
    def get_mesh_mfn(cls, transform_name):
        """
        ��ȡָ���任�ڵ��shape�ڵ��MFnMesh���Ͷ���
        Args:
            transform_name ��str����Ҫ��ȡ�� MFnMesh �����ת���ڵ�����ơ�
        Returns:
            om.MFnMesh: ��ת���ڵ������ MFnMesh ����
        """
        sel_list = om.MSelectionList()
        sel_list.add(transform_name)
        dag = om.MDagPath()
        sel_list.getDagPath(0, dag)

        dag.extendToShape()
        fn_mesh = om.MFnMesh(dag)

        return fn_mesh

    def __init__(self, ray_vector, ray_source=None, space=om.MSpace.kWorld, max_param=99999, both_directions=False,
                 mod=None):
        """
        OpenMaya.Api1.0�����ߺ����ࡣ
        Args:
        ray_vector (OpenMaya.MFloatVector): ����������
        ray_source (list, OpenMaya.MFloatPoint): ���ߵ���㡣���δ�ṩ����ʹ�����������ĵ�һ���㡣
        space (OpenMaya.MSpace, optional): ���е�����ļ���ռ䡣Ĭ��ֵΪom.MSpace.kWorld��
        max_param (float, optional): ���߷����������ֵ��Ĭ��ֵΪ 99999.
        both_directions (bool, optional): ���Ϊ True�������ߴ�Դ���������������Ͷ�䡣Ĭ��ֵΪ False��
        mod (str, optional): ���ָ����ֻ���ָ����ģ�ͣ������ⳡ��������ģ�͡�Ĭ��ֵΪ None��
        """
        self._ray_vector = om.MFloatVector()
        self._ray_source = om.MFloatPoint()
        self._space = space
        self._max_param = max_param
        self._both_directions = both_directions

        self.set_ray_vector(ray_vector)
        if ray_source:
            self.set_ray_source(ray_source)
        else:
            self._ray_source = om.MFloatPoint(ray_vector[0][0], ray_vector[0][1], ray_vector[0][2])
        self.set_mod(mod)

        self._info_dir = {}

    def set_ray_vector(self, val):
        """
        ��������ֵ��������������
        Args:
            val: ���������б���б�ÿ���б��������������������һ�� OpenMaya.MFloatVector ��һ�� OpenMaya.MVector��
        Returns:
            None
        """
        if isinstance(val, om.MFloatVector):
            self._ray_vector = val
        elif isinstance(val, om.MVector):
            self._ray_vector = om.MFloatVector(val)
        elif len(val) == 2 and len(val[0]) == 3 and len(val[1]) == 3 and MeshRay.is_float_lis(val):
            self._ray_vector = om.MFloatVector(val[1][0] - val[0][0],
                                               val[1][1] - val[0][1],
                                               val[1][2] - val[0][2])
        else:
            feedback('����{}����ӦΪ[[float, float, float], [float, float, float]]��OpenMaya.MFloatVector��OpenMaya.MVector\n'
                     'ʵ��Ϊ{}'.format(val, [list(map(type, sublist)) for sublist in val]), error=True)

    @property
    def get_ray_vector(self):
        """
        ��ȡ�����������ԡ�
        Returns:
        Vector: ����������
        """
        feedback(self._ray_vector)
        return self._ray_vector

    def set_ray_source(self, val):
        """
        ��������ֵ��������Դ�㡣
        Args:
        val: Ҫ����Ϊ����Դ��ֵ��Ӧ�����������������б�һ�� OpenMaya.MPoint���� OpenMaya.MFloatPoint��
        """
        if isinstance(val, om.MFloatPoint):
            self._ray_source = val
        elif isinstance(val, om.MPoint):
            self._ray_source = om.MFloatPoint(val)
        elif len(val) == 3 and MeshRay.is_float_lis(val):
            self._ray_source = om.MFloatPoint(val[0], val[1], val[2])
        else:
            feedback('����{}����ӦΪ[float, float, float]��OpenMaya.MFloatPoint��OpenMaya.MPoint\n'
                     'ʵ��Ϊ{}'.format(val, [list(map(type, sublist)) for sublist in val]), error=True)

    @property
    def get_ray_source(self):
        """
        ���ڷ�������Դ��� Getter ������
        """
        feedback(self._ray_source)
        return self._ray_source

    def set_space(self, val):
        """
        ʹ���ṩ��ֵ����space���ԡ�
        Parameters:
        val (om.MSpace): Ҫ�� space ��������Ϊ��ֵ��
        """
        if isinstance(val, om.MSpace):
            self._space = val
        else:
            feedback('����{}����ӦΪOpenMaya.MSpace��ʵ��Ϊ{}'.format(val, type(val)), warning=True)

    @property
    def get_space(self):
        """
        space ���Ե� Getter ������
        Returns:
        int: ��ȡ����space ���Ե�ֵ��
        """
        feedback(self._space)
        return self._space

    def set_max_param(self, val):
        """
        �����������롣
        Args:
        val (int): Ҫ���þ����ֵ��
        """
        if isinstance(val, int):
            self._max_param = val
        else:
            feedback('����{}����ӦΪint��ʵ��Ϊ{}'.format(val, type(val)), warning=True)

    @property
    def get_max_param(self):
        """
        ��������� Getter ����.
        Returns:
            int: ���������ֵ��
        """
        feedback(self._max_param)
        return self._max_param

    def set_both_directions(self, val):
        """
        �����Ƿ�����������������
        Args:
            val (bool): Ϊboth_directions���õĲ���ֵ��
        """
        if isinstance(val, bool):
            self._both_directions = val
        else:
            feedback('����{}bool��ʵ��Ϊ{}'.format(val, type(val)), warning=True)

    @property
    def get_both_directions(self):
        """
        ��ȡboth_directions��ֵ��
        Returns:
        bool: both_directions��ֵ��
        """
        feedback(self._both_directions)
        return self._both_directions

    def set_mod(self, val):
        """
        ����ָ���ļ��ģ�͡�
        ��� val �� om.MFnMesh�������η�����Ϊ val��
        ��� val �Ǳ�ʾģ�͵�transform�ڵ�����ƣ��Զ�ת��ģ�͵�shapeΪ MFnMesh��
        ��� val ���������������������η�����Ϊ None���Ҳ��Ծ���ģ������⣬���Ǽ������ģ�͡�
        Args:
        - val: ������ OpenMaya.MFnMesh ��ģ�͵�transform�ڵ�����ơ�
        """
        if isinstance(val, om.MFnMesh):
            self._mod = val
        elif isinstance(val, str):
            if (not mc.objExists(val) or mc.objectType(val) != 'transform' or
                    mc.objectType(mc.listRelatives(val, s=True)[0]) != 'mesh'):
                feedback('{}�����ڻ�Ϊģ�͵�transform�ڵ����ģ�Ͷ��������'.format(val), error=True)
            try:
                self._mod = MeshRay.get_mesh_mfn(val)
            except Exception as e:
                feedback(e, error=True)
        else:
            self._mod = None

    @property
    def get_mod(self):
        """
        mod ���Ե� getter ������

        Returns:
        int: mod ���Ե�ֵ��
        """
        feedback(self._mod)
        return self._mod

    def __shooting_core(self, fn_mesh):
        """
        ִ�����߼������Բ��Ҹ�������������Ľ��㡣
        Parameters:
        fn_mesh (om.MFnMesh): Ҫ����ִ�н���������OpenMaya.MFnMesh����
        Returns:
        tuple: �������е�����������Ԫ�飬���е�������Դ�ľ��룬
               ���е��������ID�����е������������ID��
        """
        hit_point = om.MFloatPoint()  # ���е����������

        hitDistance = om.MScriptUtil(0.0)
        hit_ray_param = hitDistance.asFloatPtr()  # ���е��뷢���ľ���

        hitFace = om.MScriptUtil()
        hit_face_ptr = hitFace.asIntPtr()  # ���е�����id
        hitTriangle = om.MScriptUtil()
        hit_triangle_ptr = hitTriangle.asIntPtr()  # ���е�����������id
        fn_mesh.closestIntersection(self._ray_source, self._ray_vector, None, None, False, self._space, self._max_param,
                                    self._both_directions, None, hit_point, hit_ray_param, hit_face_ptr,
                                    hit_triangle_ptr, None, None)

        if om.MScriptUtil().getInt(hit_face_ptr):
            return hit_point, hit_ray_param, hit_face_ptr, hit_triangle_ptr
        else:
            return None

    def get_hit_mod(self):
        """
        �˺������� mod �����������Ϣ��
        ��������� mod ����������� mod �ļ�����״����������Ϣ��
        ���δ���� mod ����������������Բ���������󲢼���ÿ�������������Ϣ��
        Returns:
        None
        """
        self._info_dir.clear()
        if self._mod:
            ret = self.__shooting_core(self._mod)
            if not ret:
                return None
            self._info_dir[om.MFnDependencyNode(self._mod.object()).name()] = {'pos': ret[0], 'distance': ret[1],
                                                                               'face_id': ret[2],
                                                                               'triangular_id': ret[3]}
        else:
            it = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kMesh)
            while not it.isDone():
                current_obj = it.currentItem()
                if current_obj.hasFn(om.MFn.kMesh):
                    dag_path = om.MDagPath()
                    it.getPath(dag_path)
                    #�����ʹ��dag_path����MFnMesh������closestIntersectionʱ����Must have a DAG path to do world space transforms
                    fn_mesh = om.MFnMesh(dag_path)
                    ret = self.__shooting_core(fn_mesh)
                    if not ret:
                        continue
                    self._info_dir[om.MFnDependencyNode(current_obj).name()] = {'pos': ret[0], 'distance': ret[1],
                                                                                'face_id': ret[2],
                                                                                'triangular_id': ret[3]}

                it.next()

    def decorator_hit(fun):
        """
        ����һ��װ���������������á�get_hit_mod����Ȼ��������뺯����fun����
        Args:
        - fun: Ҫװ�εĺ�����
        Returns:
        - �������ء�
        """
        def wrapper(self, *args, **kwargs):
            self.get_hit_mod()
            return fun(self, *args, **kwargs)
        return wrapper

    @property
    @decorator_hit
    def get_all_info(self):
        """
        ��ȡ�������߼���������Ϣ��
        Returns:
        str: �������߼���������Ϣ���ֵ䡣
        """
        return self._info_dir

    @property
    @decorator_hit
    def get_pos(self):
        """
        ��ȡÿ��������ģ�͵�������Ϣ��
        Returns:
        dict: ����ģ������Ϊ�������е�����λ����Ϣ��OpenMaya.MFloatPoint���ͣ���Ϊֵ���ֵ䡣
        """
        ret_dir = {}
        for mod, val in self._info_dir.items():
            ret_dir[mod] = val['pos']

        return ret_dir

    @property
    @decorator_hit
    def get_distance(self):
        """
       ��ȡÿ��������ģ�;��뷢��Դ�ľ��롣
       Returns:
           dict: ����ģ������Ϊ�������е㵽����Դ�ľ��루float *���ͣ���Ϊֵ���ֵ䡣
       """
        ret_dir = {}
        for mod, val in self._info_dir.items():
            ret_dir[mod] = val['distance']

        return ret_dir

    @property
    @decorator_hit
    def get_face_id(self):
        """
        ��ȡÿ��������ģ�͵����id��
        Returns:
            dict: ����ģ������Ϊ�������������id��int *���ͣ���Ϊֵ���ֵ䡣
        """
        ret_dir = {}
        for mod, val in self._info_dir.items():
            ret_dir[mod] = val['face_id']

        return ret_dir

    @property
    @decorator_hit
    def get_triangle_id(self):
        """
        ��ȡÿ��������ģ�͵�����������id��
        Returns:
            dict: ����ģ������Ϊ�����������������id��int *���ͣ���Ϊֵ���ֵ䡣
        """
        ret_dir = {}
        for mod, val in self._info_dir.items():
            ret_dir[mod] = val['triangular_id']

        return ret_dir

    def __repr__(self):
        """
        ���ַ������ص�ǰʵ���ĸ�������ֵ�ͱ���⵽����Ϣ��
        Returns:
        str: ��������ֵ�ͱ���⵽����Ϣ��
        """
        ret = 'vay_vector : {};vay_source : {};space : {};max_param : {};both_directions : {};mod : {}'.format(
            self._ray_vector, self._ray_source, self._space, self._max_param, self._both_directions, self._mod)
        return ret + '\n' + str(self._info_dir)


if __name__ == '__main__':
    tmp = MeshRay([[1, 0, 0], [0, 0, 0]], mod='pCube1')
    print(tmp.get_all_info)
    print(tmp.get_pos)
    print(tmp.get_distance)
    print(tmp.get_face_id)
    print(tmp.get_triangle_id)
    for inf in tmp.get_pos.values():
        for aix in inf:
            print(aix)
    for inf in tmp.get_distance.values():
        print(om.MScriptUtil().getFloat(inf))
    for inf in tmp.get_face_id.values():
        print(om.MScriptUtil().getInt(inf))
    for inf in tmp.get_triangle_id.values():
        print(om.MScriptUtil().getInt(inf))
