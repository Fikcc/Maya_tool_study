# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import pdb

nodeName = 'fromMeshGetDistance'  #�ڵ�������Ҳ�ǽڵ������ļ����ǲ��������
nodeId = om.MTypeId(0x00004)  #���� Maya �������ͱ�ʶ����


def feedback(txt, info=False, warning=False, error=False, block=True):
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

    if not info and not warning and not error:
        info = True
    if info:
        om.MGlobal.displayInfo('{}'.format(txt))
    elif warning:
        om.MGlobal.displayWarning('{}'.format(txt))
    elif error:
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
            val.normalize()
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
        else:
            #feedback('{}�����ڻ�Ϊģ�͵�transform�ڵ����ģ�Ͷ��������'.format(val), error=True)
            self._mod = None

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
        # else:
        #     it = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kMesh)
        #     while not it.isDone():
        #         current_obj = it.currentItem()
        #         if current_obj.hasFn(om.MFn.kMesh):
        #             dag_path = om.MDagPath()
        #             it.getPath(dag_path)
        #             #�����ʹ��dag_path����MFnMesh������closestIntersectionʱ����Must have a DAG path to do world space transforms
        #             fn_mesh = om.MFnMesh(dag_path)
        #             ret = self.__shooting_core(fn_mesh)
        #             if not ret:
        #                 continue
        #             self._info_dir[om.MFnDependencyNode(current_obj).name()] = {'pos': ret[0], 'distance': ret[1],
        #                                                                         'face_id': ret[2],
        #                                                                         'triangular_id': ret[3]}
        #
        #         it.next()

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

    @decorator_hit
    def get_all_info(self):
        """
        ��ȡ�������߼���������Ϣ��
        Returns:
        str: �������߼���������Ϣ���ֵ䡣
        """
        return self._info_dir

    @decorator_hit
    def get_pos(self):
        """
        ��ȡÿ��������ģ�͵�������Ϣ��
        Returns:
        dict: ����ģ������Ϊ�������е�����λ����Ϣ��OpenMaya.MFloatPoint���ͣ���Ϊֵ���ֵ䡣
        """
        ret_dir = {}
        for mod, val in self._info_dir.items():
            return val['pos']

        return ret_dir

    @decorator_hit
    def get_distance(self):
        """
       ��ȡÿ��������ģ�;��뷢��Դ�ľ��롣
       Returns:
           dict: ����ģ������Ϊ�������е㵽����Դ�ľ��루float *���ͣ���Ϊֵ���ֵ䡣
       """
        ret_dir = {}
        for mod, val in self._info_dir.items():
            return val['distance']

        return None
        #return ret_dir

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



class WoDongNode(ompx.MPxNode):
    rayMesh = om.MObject()#ģ�Ͷ���
    sourceArray = om.MObject()#����Դ��
    targetArray = om.MObject()#�����յ�
    startArray = om.MObject()#�����
    outDistance = om.MObject()  #����㵽ģ�͵ľ���



    @classmethod
    def update_attr_properties(cls, attr):
        attr.setWritable(True)#���Կ�д
        attr.setStorable(True)#�ɴ���
        attr.setReadable(True)#�ɶ�
        attr.setConnectable(True)
        if attr.type() == om.MFn.kNumericAttribute:  #�����������������
            attr.setKeyable(True)#��k֡

    @classmethod
    def creatorNode(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def nodeInitialize(cls):
        """
        ��ʼ���ڵ�
        :return:
        """
        typeAttr = om.MFnTypedAttribute()
        numAttr = om.MFnNumericAttribute()
        compAttr = om.MFnCompoundAttribute()

        WoDongNode.rayMesh = typeAttr.create("inputMesh", "inMesh", om.MFnData.kMesh)
        cls.update_attr_properties(typeAttr)
        WoDongNode.addAttribute(WoDongNode.rayMesh)

        WoDongNode.sourceArray_x = numAttr.create("sourceArray_x", "sorArry_x", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.sourceArray_x)

        WoDongNode.sourceArray_y = numAttr.create("sourceArray_y", "sorArry_y", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.sourceArray_y)

        WoDongNode.sourceArray_z = numAttr.create("sourceArray_z", "sorArry_z", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.sourceArray_z)

        WoDongNode.sourceArray = numAttr.create("sourceArray", "sorArry", WoDongNode.sourceArray_x,
                                                WoDongNode.sourceArray_y, WoDongNode.sourceArray_z)
        WoDongNode.addAttribute(WoDongNode.sourceArray)#������ʼ��

        WoDongNode.targetArray_x = numAttr.create("targetArray_x", "tagArry_x", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.targetArray_x)

        WoDongNode.targetArray_y = numAttr.create("targetArray_y", "tagArry_y", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.targetArray_y)

        WoDongNode.targetArray_z = numAttr.create("targetArray_z", "tagArry_z", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.targetArray_z)

        WoDongNode.targetArray = numAttr.create("targetArray", "tagArry", WoDongNode.targetArray_x,
                                                WoDongNode.targetArray_y, WoDongNode.targetArray_z)
        WoDongNode.addAttribute(WoDongNode.targetArray)#�����յ�

        WoDongNode.array = compAttr.create("array", "arry")
        cls.update_attr_properties(compAttr)
        compAttr.addChild(WoDongNode.sourceArray)
        compAttr.addChild(WoDongNode.targetArray)
        WoDongNode.addAttribute(WoDongNode.array)#��������

        WoDongNode.startArray_x = numAttr.create("startArray_x", "starArry_x", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.startArray_x)

        WoDongNode.startArray_y = numAttr.create("startArray_y", "starArry_y", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.startArray_y)

        WoDongNode.startArray_z = numAttr.create("startArray_z", "starArry_z", om.MFnNumericData.kFloat, 0.0)
        WoDongNode.addAttribute(WoDongNode.startArray_z)

        WoDongNode.startArray = numAttr.create("startArray", "starArry", WoDongNode.startArray_x,
                                                WoDongNode.startArray_y, WoDongNode.startArray_z)

        cls.update_attr_properties(numAttr)
        WoDongNode.addAttribute(WoDongNode.startArray)#�����

        WoDongNode.outDistance = numAttr.create("Distance", "dis", om.MFnNumericData.kFloat, 0.0)
        numAttr.setReadable(True)
        numAttr.setWritable(False)
        numAttr.setStorable(True)
        numAttr.setKeyable(False)
        WoDongNode.addAttribute(WoDongNode.outDistance)#�������

        WoDongNode.attributeAffects(WoDongNode.rayMesh, WoDongNode.outDistance)
        WoDongNode.attributeAffects(WoDongNode.array, WoDongNode.outDistance)
        WoDongNode.attributeAffects(WoDongNode.startArray, WoDongNode.outDistance)

    def __init__(self):
        super(WoDongNode, self).__init__()
        self.ray = MeshRay([[0, 0, 0], [0, 0, 0]], [0, 0, 0], both_directions=True)

    def compute(self, plug, dataBlok):
        if plug == WoDongNode.outDistance:
            #mfn_mesh = dataBlok.inputValue(WoDongNode.rayMesh).asMesh()
            mfn_mesh = self.get_upstream_nod()
            sor_array = dataBlok.inputValue(WoDongNode.sourceArray).asFloat3()
            tag_array = dataBlok.inputValue(WoDongNode.targetArray).asFloat3()
            star_array = dataBlok.inputValue(WoDongNode.startArray).asFloat3()
            outputAttr = dataBlok.outputValue(WoDongNode.outDistance)

            lis_array = list(map(lambda x, y:y-x, sor_array, tag_array))
            lis_start = list(map(lambda x:round(x, 5), star_array))
            if mfn_mesh:
                vector_fVector = om.MFloatVector(lis_array[0], lis_array[1], lis_array[2])
                start_fPoint = om.MFloatPoint(lis_start[0], lis_start[1], lis_start[2])
                self.ray.set_ray_vector(vector_fVector)
                self.ray.set_ray_source(lis_start)
                self.ray.set_mod(mfn_mesh)
                if self.ray.get_distance():
                    distance = om.MScriptUtil().getFloat(self.ray.get_distance())
                    # pos = self.ray.get_pos()
                    # print(pos.x, pos.y, pos.z)
                    # print(distance)
                    outputAttr.setFloat(distance)
                else:
                    outputAttr.setFloat(0.0)
            else:
                outputAttr.setFloat(0.0)
        return om.kUnknownParameter

    def get_upstream_nod(self):
        """
        ��ȡ����mesh�ڵ�
        :return:
        """
        dpd_nod = om.MFnDependencyNode(self.thisMObject())
        plug = dpd_nod.findPlug('inputMesh', False)

        mit = om.MItDependencyGraph(plug, om.MFn.kMesh, om.MItDependencyGraph.kUpstream,
                                    om.MItDependencyGraph.kDepthFirst, om.MItDependencyGraph.kNodeLevel)
        mesh_node = None
        while not mit.isDone():
            mesh_node = mit.thisNode()
            break

        if isinstance(mesh_node, om.MObject):
            fn_dag_node = om.MFnDagNode(mesh_node)
            dag_node = om.MDagPath()
            fn_dag_node.getPath(dag_node)
            return om.MFnMesh(dag_node)
        return None

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
