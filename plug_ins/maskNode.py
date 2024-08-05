#coding=gbk
import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

import maya.cmds as mc

from datetime import datetime
import os

def maya_useNewAPI():
    pass


class DongShotMaskLocator(omui.MPxLocatorNode):

    NAME = "DongShotMask"
    TYPE_ID = om.MTypeId(0x0007F7FE)

    DRAW_DB_CLASSIFICATION = "drawdb/geometry/zurbriggshotmask"
    DRAW_REGISTRANT_ID = "DongShotMaskLocator"

    TEXT_ATTR = [('topLeftText', 'tlt', u'�����ַ�'), ('topCenterText', 'tct', u'�����ַ�'), ('topRightText', 'trt', u'�����ַ�'),
                 ('bottomLeftText', 'blt', u'�����ַ�'), ('bottomCenterText', 'bct', u'�����ַ�'), ('bottomRightText', 'brt', u'�����ַ�')]

    def postConstructor(self):
        """
        ��д�������������������ڴ���ʱ�رգ�������ʹ��ʱ�޷����������еĵƹ���Ӱ
        :return:
        """
        node_fn = om.MFnDependencyNode(self.thisMObject())
        node_fn.findPlug('castsShadows', False).setBool(False)
        node_fn.findPlug('receiveShadows', False).setBool(False)
        node_fn.findPlug('motionBlur', False).setBool(False)

    @classmethod
    def creator(cls):
        """
        �����ڵ�ʵ���ķ���
        :return:
        """
        return DongShotMaskLocator()

    @classmethod
    def initialize(cls):
        """
        ��ʼ���ڵ�ķ���
        :return:
        """
        numeric_attr = om.MFnNumericAttribute()#�������Զ���
        type_attr = om.MFnTypedAttribute()#�ַ����Զ���
        string_data_fn = om.MFnStringData()#�ַ������󣬲�����������

        #�����������ֵ����������
        dft = string_data_fn.create('')#Ĭ�������ֵ
        camera_name = type_attr.create('camera', 'cam', om.MFnData.kString, dft)#��������
        type_attr.setNiceNameOverride(u'���')#����niceName
        cls.update_attr_properties(type_attr)
        cls.addAttribute(camera_name)

        #�������ϻ��Ƶ��ַ�����
        for i, inf in enumerate(cls.TEXT_ATTR):
            dft = string_data_fn.create('Position {}'.format(str(i+1).zfill(2)))
            position = type_attr.create(inf[0], inf[1], om.MFnData.kString, dft)
            type_attr.setNiceNameOverride(inf[2])
            cls.update_attr_properties(type_attr)
            cls.addAttribute(position)

        #�ı��������
        text_padding = numeric_attr.create('textPadding', 'tp', om.MFnNumericData.kShort, 10)
        numeric_attr.setNiceNameOverride(u'�ַ��߾�')
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0)
        numeric_attr.setMax(50)
        cls.addAttribute(text_padding)

        #�ַ�����
        dft = string_data_fn.create('consolas')
        font_name = type_attr.create('fontName', 'fn', om.MFnData.kString, dft)
        type_attr.setNiceNameOverride(u'�ַ�����')
        cls.update_attr_properties(type_attr)
        cls.addAttribute(font_name)

        #�ַ���ɫ
        font_color = numeric_attr.createColor('fontColor', 'fc')
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setNiceNameOverride(u'�ַ���ɫ')
        numeric_attr.default = (1.0, 1.0, 1.0)
        cls.addAttribute(font_color)

        #�ַ�͸����
        font_alpha = numeric_attr.create('fontAlpha', 'fa', om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setNiceNameOverride(u'�ַ�͸����')
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute((font_alpha))

        #�ַ���С
        font_scale = numeric_attr.create('fontScale', 'fs', om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setNiceNameOverride(u'�ַ���С')
        numeric_attr.setMin(0.1)
        numeric_attr.setMax(2.0)
        cls.addAttribute(font_scale)

        #�ֱ��������ϱ߾�
        top_border = numeric_attr.create('topBorder', 'tbd', om.MFnNumericData.kBoolean, True)
        numeric_attr.setNiceNameOverride(u'�ֱ�����������')
        cls.update_attr_properties(numeric_attr)
        cls.addAttribute(top_border)

        #�ֱ��������±߾�
        bottom_border = numeric_attr.create('buttomBorder', 'bbd', om.MFnNumericData.kBoolean, True)
        numeric_attr.setNiceNameOverride(u'�ֱ�����������')
        cls.update_attr_properties(numeric_attr)
        cls.addAttribute(bottom_border)

        #�߿���ɫ
        border_color = numeric_attr.createColor('borderColor', 'bc')
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setNiceNameOverride(u'�ֱ�����������ɫ')
        numeric_attr.default = (0.0, 0.0, 0.0)
        cls.addAttribute(border_color)

        #�߿�͸����
        border_alpha = numeric_attr.create('borderAlpha', 'ba', om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setNiceNameOverride(u'�ֱ���������͸����')
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(border_alpha)

        #�߿�����
        border_scale = numeric_attr.create('borderScale', 'bs', om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setNiceNameOverride(u'�ֱ�������������')
        numeric_attr.setMin(0.5)
        numeric_attr.setMax(2.0)
        cls.addAttribute(border_scale)

        #���������
        counter_padding = numeric_attr.create('counterPadding', 'cpd', om.MFnNumericData.kShort, 4)
        numeric_attr.setNiceNameOverride(u'֡�����')
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(1)
        numeric_attr.setMax(6)
        cls.addAttribute(counter_padding)

    @classmethod
    def update_attr_properties(cls, attr):
        attr.writable = True#���Կ�д
        attr.storable = True#�ɴ���
        if attr.type() == om.MFn.kNumericAttribute:#�����������������
            attr.keyable = True #��k֡

    def __init__(self):
        super(DongShotMaskLocator, self).__init__()

    def excludeAsLocator(self):
        return False



class DongShotMaskData(om.MUserData):
    """
    �û����ݻ���
    """
    def __init__(self):
        super(DongShotMaskData, self).__init__(False)
        self.parsed_fields = []

        self.current_time = 0
        self.counter_padding = 4

        self.font_name = "Consolas"#�ַ�����
        self.font_color = om.MColor((1.0, 1.0, 1.0))
        self.font_scale = 1.0
        self.text_padding = 10#���Ҳ��ַ�����ֱ����ű߽�ľ���

        self.top_border = True
        self.bottom_border = True
        self.border_color = om.MColor((0.0, 0.0, 0.0))
        self.border_scale = 1.0

        self.vp_width = 0#�������������أ��������ͼ�����Ͻǡ�ԭ�������������ͼ��ԭ��
        self.vp_height = 0

        self.mask_width = 0#�ֱ��������ֵĵ����سߴ硣ԭ���Ƿֱ����ŵ���ʼ��Ⱦԭ�㣬���������������ͼ����ʼԭ��
        self.mask_height = 0

    def __str__(self):
        output = ''
        output += u'text��{}\n'.format(self.parsed_fields)

        output += u'Current Time��{}\n'.format(self.current_time)
        output += u'Counter Padding��{}\n'.format(self.counter_padding)

        output += u'Font Color��{}\n'.format(self.font_color)
        output += u'Font Scale��{}\n'.format(self.font_scale)
        output += u'Text Padding��{}\n'.format(self.text_padding)

        output += u'Top Border��{}\n'.format(self.top_border)
        output += u'Bottom Border��{}\n'.format(self.bottom_border)
        output += u'Border Color��{}\n'.format(self.border_color)

        return output.encode('unicode_escape').decode()


class DongMaskDrawOverride(omr.MPxDrawOverride):
    """
    MPxDrawOverride�������Զ���Ļ��Ƹ����߼�
    """
    NAME = "donghotmask_draw_override"

    @staticmethod
    def camera_transform_name(camera_path):
        camera_transform = camera_path.transform()
        if camera_transform:
            return om.MFnTransform(camera_transform).name()
        return ''

    @staticmethod
    def camera_shape_name(camera_path):
        camera_shape = camera_path.node()
        if camera_shape:
            return om.MFnCamera(camera_shape).name()
        return ''

    @staticmethod
    def creator(obj):
        return DongMaskDrawOverride(obj)

    def __init__(self, obj):
        super(DongMaskDrawOverride, self).__init__(obj, None)

        self.parsed_fields = []

    def supportedDrawAPIs(self):
        return (omr.MRenderer.kAllDevices)

    def hasUIDrawables(self):
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        """
        ��ͼ׼��
        :param obj_path:�������Զ���ڵ���
        :param camera_path:��ǰʹ�õ����shape��
        :param frame_context:������ǰ��Ⱦ֡��һЩȫ����Ϣ
        :param old_data:�û���Ϣ�����
        :return:
        """
        data = old_data
        if not isinstance(data, DongShotMaskData):
            data = DongShotMaskData()#����������

        dag_fn = om.MFnDagNode(obj_path)#�Զ���ڵ����
        camera_name = dag_fn.findPlug('camera', False).asString()
        #���������ǳ����ڵ�����任���ƻ�Ϊ�ն�����������������
        if camera_name and self.camera_exists(camera_name) and not self.is_camera_match(camera_path, camera_name):
            return None#�������еľ�������������������������ͬʱ��������

        #���û���Ϣ���е�����ȡֵ���ӽڵ��������
        data.current_time = int(mc.currentTime(q=True))
        data.counter_padding = dag_fn.findPlug('counterPadding', False).asInt()
        data.text_padding = dag_fn.findPlug('textPadding', False).asInt()
        data.font_name = dag_fn.findPlug('fontName', False).asString()

        r = dag_fn.findPlug('fontColorR', False).asFloat()
        g = dag_fn.findPlug('fontColorG', False).asFloat()
        b = dag_fn.findPlug('fontColorB', False).asFloat()
        a = dag_fn.findPlug('fontAlpha', False).asFloat()
        data.font_color = om.MColor((r, g, b, a))
        data.font_scale = dag_fn.findPlug('fontScale', False).asFloat()

        r = dag_fn.findPlug('borderColorR', False).asFloat()
        g = dag_fn.findPlug('borderColorG', False).asFloat()
        b = dag_fn.findPlug('borderColorB', False).asFloat()
        a = dag_fn.findPlug('borderAlpha', False).asFloat()
        data.border_color = om.MColor((r, g, b, a))
        data.border_scale = dag_fn.findPlug('borderScale', False).asFloat()

        data.top_border = dag_fn.findPlug('topBorder', False).asBool()
        data.bottom_border = dag_fn.findPlug('buttomBorder', False).asBool()

        #��ȡ�����ͼ�ĳߴ磬ԭ�������Ͻǡ�[0, 0, �����ظ���, �����ظ���]
        vp_x, vp_y, data.vp_width, data.vp_height = frame_context.getViewportDimensions()
        if not (data.vp_width and data.vp_height):#�������ߴ�Ϊ0
            return None
        data.mask_width, data.mask_height = self.get_mask_width_height(camera_path, data.vp_width, data.vp_height)
        if not (data.mask_width and data.mask_height):
            return None

        data.parsed_fields = []#���ַ��б��������ַ�����������ַ�ʱȡ��
        for inf in DongShotMaskLocator.TEXT_ATTR:
            orig_text = dag_fn.findPlug(inf[0], False).asString()#��ȡ�ڵ��и����Ե�ֵ
            parsed_text = self.parse_text(orig_text, camera_path, data)
            data.parsed_fields.append(parsed_text)

        return data#��ͬʱ�������û���Ϣ

    def get_mask_width_height(self, camera_path, vp_width, vp_height):
        """
        ��ȡ���ֵĿ��
        :param camera_path:�������
        :param vp_width: #�����ͼ��ȣ����أ�
        :param vp_height:#�����ͼ�߶�
        :return:�ֱ����ŵ����ߴ������������ͼ�е�����λ��
        """
        camera_fn = om.MFnCamera(camera_path)
        device_aspect_ratio = mc.getAttr('defaultResolution.deviceAspectRatio')#��߱�
        camera_aspect_ratio = camera_fn.aspectRatio()
        vp_aspect_ratio = vp_width/float(vp_height)
        scale = 1.0

        #overscan���Ե�ֵ����Ⱦ��ĳ�ߵ������ͼ��߽�ı�ֵ��δ�򿪷ֱ�����ʱΪ1����ʱĬ��Ϊ1.3�������Կ��������shape��displayOptions�п���
        #camera_fn.filmFit��ָ���shape��fitResolutionGateö�����ԡ�Horizontal����֤��Ϊoverscan�ı�ֵ��Vertical����֤��Ϊoverscan�ı�ֵ
        if camera_fn.filmFit == om.MFnCamera.kHorizontalFilmFit:#�����ֵʱ
            mask_width = vp_width/camera_fn.overscan#�����ֺ󣬷ֱ����ŵ���Ⱦ�ߴ�
            mask_height = mask_width/device_aspect_ratio
        elif camera_fn.filmFit == om.MFnCamera.kVerticalFilmFit:#���߶�ֵʱ
            mask_height = vp_height/camera_fn.overscan
            mask_width = mask_height*device_aspect_ratio
        elif camera_fn.filmFit == om.MFnCamera.kFillFilmFit:#��䣬�ֱ����ſ��ܻ�ֱ�Ӷ�����ͼ�߽�
            if vp_aspect_ratio<device_aspect_ratio:
                if camera_aspect_ratio<device_aspect_ratio:
                    scale = camera_aspect_ratio/vp_aspect_ratio
                else:
                    scale = device_aspect_ratio/vp_aspect_ratio
            elif camera_aspect_ratio>device_aspect_ratio:
                scale = device_aspect_ratio/camera_aspect_ratio

            mask_width = vp_width / camera_fn.overscan*scale
            mask_height = mask_width / device_aspect_ratio
        elif camera_fn.filmFit == om.MFnCamera.kOverscanFilmFit:#������С�߾࣬�ֱ���������ͼ�߽���ӽ��ķ���Ҳ�ᱣ����С����
            if vp_aspect_ratio<device_aspect_ratio:
                if camera_aspect_ratio<device_aspect_ratio:
                    scale = camera_aspect_ratio/vp_aspect_ratio
                else:
                    scale = device_aspect_ratio/vp_aspect_ratio
            elif camera_aspect_ratio>device_aspect_ratio:
                scale = device_aspect_ratio/camera_aspect_ratio

            mask_height = vp_height / camera_fn.overscan/scale
            mask_width = mask_height * device_aspect_ratio
        else:
            om.MGlobal.displayError(u'��֧�ֵ���Ϸֱ����ţ�{}��'.format(camera_fn.filmFit))
            return None, None

        return mask_width, mask_height

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        """
        �������л��Ʋ���
        :param obj_path:
        :param draw_manager:
        :param frame_context:
        :param data:
        :return:
        """
        if not (data and isinstance(data, DongShotMaskData)):
            return
        #�����ͼ��ԭ��(0, 0)�����½�
        vp_half_width = 0.5*data.vp_width#�����ͼ��һ���
        vp_half_height = 0.5*data.vp_height#�����ͼ��һ���

        mask_half_width = 0.5*data.mask_width#�ֱ����ŵ�һ���
        mask_x = vp_half_width-mask_half_width#���ֺ���x����ʼ��

        mask_half_height = 0.5*data.mask_height#�ֱ����ŵ�һ���
        mask_bottom_y = vp_half_height-mask_half_height#��������y����ʼ��
        mask_top_y = vp_half_height+ mask_half_height#�ֱ��������·��ĸ�

        border_height = int(0.05 * data.mask_height*data.border_scale)#�ֱ��������ֵĸ߶�
        background_size = (int(data.mask_width), border_height)
        font_size = int(0.85*border_height*data.font_scale)

        draw_manager.beginDrawable()#��ʼ��
        #���Ʒֱ������ڵ�����
        if data.top_border:#��������֣���Ϊԭ�������Ͻǣ�����y���ֵ���·���
            #����Ҫ��ͬһ��λ�û����������ݣ���������ֺ���������֣�������MPoint�м����0.1������api֪��˭��˭�����档ֵԽС������������Խ��ǰ��ֵԽ��Խ�ڵײ�
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_top_y-border_height, 0.1), background_size, data.border_color)
        if data.bottom_border:#�Ϸ����֡�
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y, 0.1), background_size, data.border_color)

        #���Ʒֱ������������ϵ��ַ�
        draw_manager.setFontName(data.font_name)
        draw_manager.setFontSize(font_size)

        #������ͼ�·����ַ�
        self.draw_label(draw_manager, om.MPoint(mask_x+data.text_padding, mask_top_y - border_height, 0.0), data, 0,
                        omr.MUIDrawManager.kLeft, background_size)
        self.draw_label(draw_manager, om.MPoint(vp_half_width, mask_top_y-border_height, 0.0), data, 1,
                        omr.MUIDrawManager.kCenter, background_size)
        self.draw_label(draw_manager, om.MPoint(mask_x +data.mask_width- data.text_padding, mask_top_y - border_height, 0.0), data, 2,
                        omr.MUIDrawManager.kRight, background_size)
        #������ͼ�Ϸ����ַ�
        self.draw_label(draw_manager, om.MPoint(mask_x + data.text_padding, mask_bottom_y, 0.0), data, 3,
                        omr.MUIDrawManager.kLeft, background_size)
        self.draw_label(draw_manager, om.MPoint(vp_half_width, mask_bottom_y, 0.0), data, 4,
                        omr.MUIDrawManager.kCenter, background_size)
        self.draw_label(draw_manager, om.MPoint(mask_x + data.mask_width - data.text_padding, mask_bottom_y, 0.0),
                        data, 5, omr.MUIDrawManager.kRight, background_size)

        draw_manager.endDrawable()#���ƽ���

    def draw_border(self, draw_manager, position, background_size, color):
        """
        �ڷֱ������л������֣���Ϊ������ʾ������л��棬���Եλ������Ի��������죬����Ļ��ռ�ñ߿�һ�ξ���
        :param draw_manager:���ƹ���������
        :param position: ��ʼλ��
        :param background_size:�����ƿ�ȣ����Ƹ߶ȣ�
        :param color: ������ɫ
        :return:
        """
        #��ʼλ�ã��������ݣ������Ű�λ�ã�����ͼ�ߴ磬����ͼ��ɫ
        draw_manager.text2d(position, ' ', alignment=omr.MUIDrawManager.kLeft, backgroundSize=background_size, backgroundColor=color)

    def draw_label(self, draw_manager, position, data, data_index, alignment, background_size):
        if data.parsed_fields[data_index]['image_path']:#����������Ϊͼ��ʱ
            self.draw_image(draw_manager, position, data, data_index, alignment, background_size)
            return

        text = data.parsed_fields[data_index]['text']
        draw_manager.setColor(data.font_color)
        if text:#�����ַ����ַ�����Ϊ͸��
            draw_manager.text2d(position, text, alignment=alignment, backgroundSize=background_size, backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

    def draw_image(self, draw_manager, position, data, data_index, alignment, background_size):
        texture_manager = omr.MRenderer.getTextureManager()
        texture = texture_manager.acquireTexture(data.parsed_fields[data_index]['image_path'])#��ȡͼƬ�ļ�·��
        if not texture:
            om.MGlobal.displayError(u'��֧�ֵ��ļ���ʽ{}'.format(data.parsed_fields[data_index]['image_path']))
            return

        draw_manager.setTexture(texture)
        draw_manager.setTextureSampler(omr.MSamplerState.kMinMagMipLinear, omr.MSamplerState.kTexClamp)
        draw_manager.setTextureMask(omr.MBlendState.kRGBAChannels)
        draw_manager.setColor(om.MColor((1.0, 1.0, 1.0, data.font_color.a)))

        texture_desc = texture.textureDescription()
        scale_y = (0.5*background_size[1]) - 2
        scale_x = scale_y/texture_desc.fHeight*texture_desc.fWidth#ͨ��ͼƬ�������еĸ߶ȼ����ͼƬӦ�еĿ��

        if alignment == omr.MUIDrawManager.kLeft:
            position = om.MPoint(position.x+scale_x, position.y +int(0.5*background_size[1]), position.z)
        elif alignment == omr.MUIDrawManager.kRight:
            position = om.MPoint(position.x-scale_x, position.y +int(0.5*background_size[1]), position.z)
        else:
            position = om.MPoint(position.x, position.y +int(0.5*background_size[1]), position.z)

        draw_manager.rect2d(position, om.MVector(0.0, 1.0, 0.0), scale_x, scale_y, True)

    def get_scene_name(self):
        scene_name = mc.file(q=True, sn=True, shn=True)
        if scene_name:
            scene_name = os.path.splitext(scene_name)[0]
        else:
            scene_name = u'δ֪����'
        return scene_name

    def get_date(self):
        weekdays_in_chinese = {0: "����һ", 1: "���ڶ�", 2: "������", 3: "������",
                               4: "������", 5: "������", 6: "������"}
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")  # ��-��-��
        time_str = now.strftime("%H:%M")     # ʱ:��
        weekday_str = weekdays_in_chinese[now.weekday()]
        return '{}/{}/{}'.format(date_str, time_str, weekday_str)

    def get_image(self, image_path):
        image_path = image_path.strip()#�Ƴ��ַ���ͷβָ�����ַ���Ĭ��Ϊ�ո���з������ַ�����
        if os.path.exists(image_path):
            return image_path, ''
        return '', u'ͼ�񲻴���'

    def camera_exists(self, name):
        dg_iter = om.MItDependencyNodes(om.MFn.kCamera)
        while not dg_iter.isDone():
            camera_path = om.MDagPath.getAPathTo(dg_iter.thisNode())
            if self.is_camera_match(camera_path, name):
                return True

            dg_iter.next()
        return False

    def is_camera_match(self, camera_path, name):
        if self.camera_transform_name(camera_path) == name or self.camera_shape_name(camera_path) == name:
            return True
        return False

    def get_camera_focalLength(self):
        view = omui.M3dView.active3dView()
        camDag = view.getCamera()
        camera = camDag.fullPathName()
        name= mc.listRelatives(camera, parent = True)[0]
        return round(mc.getAttr('{}.focalLength'.format(name)), 3)

    def parse_text(self, orig_text, camera_path, data):
        image_path = ''
        text = orig_text#����������е��ַ�ֵ

        if '{counter}' in text:
            text = text.replace('{counter}', '{}/{}'.format(str(data.current_time).zfill(data.counter_padding), mc.playbackOptions(q=True, max=True)))
        if '{scene}' in text:
            text = text.replace('{scene}', self.get_scene_name())
        if '{date}' in text:
            text = text.replace('{date}', self.get_date())
        if '{camera}' in text:
            text = text.replace('{camera}', self.camera_transform_name(camera_path))
        if '{focalLength}' in text:
            text = text.replace('{focalLength}', u'����:{}'.format(self.get_camera_focalLength()))

        stripped_text = text.strip()#�Ƴ��ַ���ͷβָ�����ַ���Ĭ��Ϊ�ո���з������ַ�����
        if stripped_text.startswith('{image=') and stripped_text.endswith('}'):
            image_path, text = self.get_image(stripped_text[7:-1])

        return {'text': text, 'image_path':image_path}



def initializePlugin(obj):
    """
    """
    plugin_fn = om.MFnPlugin(obj, "dong", "1.0.0", "Any")

    try:
        plugin_fn.registerNode(DongShotMaskLocator.NAME,
                               DongShotMaskLocator.TYPE_ID,
                               DongShotMaskLocator.creator,
                               DongShotMaskLocator.initialize,
                               om.MPxNode.kLocatorNode,
                               DongShotMaskLocator.DRAW_DB_CLASSIFICATION)
        print(u'���{}�Ѽ���'.format(DongShotMaskLocator.NAME))
    except:
        om.MGlobal.displayError(u"�ڵ�ע��ʧ��: {0}".format(DongShotMaskLocator.NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(DongShotMaskLocator.DRAW_DB_CLASSIFICATION,
                                                      DongShotMaskLocator.DRAW_REGISTRANT_ID,
                                                      DongMaskDrawOverride.creator)
    except:
        om.MGlobal.displayError(u"�޷�ע����Ƹ���: {0}".format(DongMaskDrawOverride.NAME))


def uninitializePlugin(obj):
    """
    """
    plugin_fn = om.MFnPlugin(obj)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(DongShotMaskLocator.DRAW_DB_CLASSIFICATION, DongShotMaskLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError(u"�޷�ȡ��ע����Ƹ���: {0}".format(DongMaskDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(DongShotMaskLocator.TYPE_ID)
    except:
        om.MGlobal.displayError(u"ע���ڵ�ʧ��: {0}".format(DongShotMaskLocator.NAME))


if __name__ == "__main__":

    mc.file(f=True, new=True)

    plugin_name = "maskNode.py.py"
    mc.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    mc.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    mc.evalDeferred('cmds.createNode("DongShotMask")')