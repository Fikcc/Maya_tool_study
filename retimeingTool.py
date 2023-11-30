#coding=gbk
import maya.cmds as mc
import maya.mel as mm

from functools import partial

class RetimingUtils(object):
    @classmethod
    def set_current_time(cls, time):
        """
        ��ʱ�们�����õ�ĳһ֡��
        :param time: Ҫ���õ�֡��ֵ
        :return:
        """
        mc.currentTime(time)

    @classmethod
    def get_select_range(cls):
        """
        ������ʱ��������ѡ��֡��Χ
        :return:(��ʼ֡, ����֡)
        """
        playback_slider = mm.eval('$tempVar = $gPlayBackSlider')
        selected_range = mc.timeControl(playback_slider, q=True, rangeArray=True)

        return selected_range

    @classmethod
    def find_keyframe(cls, which, time=None):
        """
        ��ȡѡ�ж�����ϡ��¡���ǰ������֡��ֵ
        :param which:���ص�ǰѡ�ж����k֡�У���ʱ�们��Ϊ׼��ʲôλ�õ�֡��ֵ
        next����ǰʱ�们�����һ��k֡��ֵ |previous����һ��֡ |first����ǰ���֡ |last��������֡
        :param time:��ʹ����һ֡����һ��ʱ������ָ��һ��ʱ�䣬���ؽ�Ϊ��ʱ�����һ֡����һ֡�����û���޶�������ʱ�们�������һ֡
        :return:ѡ�ж���Ķ�Ӧ֡��ֵ
        """
        kwargs = {'which': which}
        if which in ['next', 'previous']:
            kwargs['time'] = (time, time)

        return mc.findKeyframe(**kwargs)

    @classmethod
    def change_keyframe_time(cls, current_time, new_time):
        """
        �ƶ�ĳ֡����һ��λ��
        :param current_time:���ƶ���֡
        :param new_time: �ƶ�����֡
        :return:
        """
        mc.keyframe(e=True, t=(current_time, current_time), tc=new_time)

    @classmethod
    def get_start_keyframe_time(cls, range_start_time):
        """
        ��ȡĳ�϶���Χ�ڵ���ʼ֡������Χ��û��֡ʱ����ȡ��Χ������ʱ�����ϵ���һ֡
        :param range_start_time: ָ�����϶���Χ
        :return: ��һ֡��ֵ
        """
        start_times = mc.keyframe(q=True, t=(range_start_time, range_start_time))
        if start_times:
            return start_times[0]
        else:
            return cls.find_keyframe('previous', range_start_time)

    @classmethod
    def get_last_keyframe_time(cls):
        """
        ��ȡ��β֡��ֵ
        :return:
        """
        return cls.find_keyframe('last')

    @classmethod
    def retime_keys(cls, retime_vlue, incremental, move_to_next):
        range_start_time, range_end_time = cls.get_select_range()#��ȡ��ѡ��Χ
        start_keyframe_time = cls.get_start_keyframe_time(range_start_time)#��ȡ��һ֡
        last_keyframe_time = cls.get_last_keyframe_time()#��ȡ���һ֡
        current_time = start_keyframe_time

        new_keyframe_times = [start_keyframe_time]
        current_keyfrmae_values = [start_keyframe_time]#ֱ��=�б���ǳ�����������ֿ����б�д���Եõ������ڴ�
        while current_time != last_keyframe_time:
            next_keyframe_time = cls.find_keyframe('next', current_time)#��ȡ��ǰ֡����һ֡
            time_diff = 0
            if incremental:#�����ӵľ���Ҫ�������о���ʱ
                time_diff = next_keyframe_time - current_time#��һ֡�뵱ǰ֡�Ĳ�
                if current_time < range_end_time:#����ǰ֡С�ڸ�����Χ��β֡
                    time_diff += retime_vlue#�ڲ�ֵ�ϵ���Ҫ�ƶ��ľ���
                    if time_diff < 1:#���ƶ�����С��1�����ƶ�������ƶ�ʱ
                        time_diff = 1
            else:
                if current_time < range_end_time:  #����ǰ֡С�ڸ�����Χ��β֡
                    time_diff = retime_vlue  #�ڲ�ֵ�ϵ���Ҫ�ƶ��ľ���
                else:
                    time_diff = next_keyframe_time - current_time

            new_keyframe_times.append(new_keyframe_times[-1] + time_diff)#�ӵ�һ֡��ʼ������Ӳ�ֵ��֡
            current_time = next_keyframe_time#����ǰ֡����Ϊ�Ѵ����֡��Ϊ��һ֡������׼��
            current_keyfrmae_values.append(current_time)#���������֡���봦����֡�б�

        if len(new_keyframe_times) > 1:
            cls.retime_keys_recursive(start_keyframe_time, 0, new_keyframe_times)

        first_keyframe_time = cls.find_keyframe('first')
        if move_to_next and range_start_time >= first_keyframe_time:
            next_keyframe_time = cls.find_keyframe('next', start_keyframe_time)
            cls.set_current_time(next_keyframe_time)
        elif range_end_time > first_keyframe_time:
            cls.set_current_time(start_keyframe_time)
        else:
            cls.set_current_time(range_start_time)

    @classmethod
    def retime_keys_recursive(cls, current_time, index, new_keyframe_times):
        if index >= len(new_keyframe_times):
            return

        updated_keyframe_time = new_keyframe_times[index]
        next_keyframe_time = cls.find_keyframe('next', current_time)
        if  updated_keyframe_time < next_keyframe_time:
            cls.change_keyframe_time(current_time, updated_keyframe_time)
            cls.retime_keys_recursive(next_keyframe_time, index+1, new_keyframe_times)
        else:
            cls.retime_keys_recursive(next_keyframe_time, index+1, new_keyframe_times)
            cls.change_keyframe_time(current_time, updated_keyframe_time)

class RetimeingUi(object):
    WINDOW_NAME = '�|'
    WINDOW_TITLE = '֡�ƶ�����'

    @classmethod
    def display(cls, development=False):
        if mc.window(cls.WINDOW_NAME, exists=True):
            mc.deleteUI(cls.WINDOW_NAME, wnd=True)

        if development and mc.windowPref(cls.WINDOW_NAME, ex=True):
            mc.windowPref(cls.WINDOW_NAME, r=True)

        main_window = mc.window(cls.WINDOW_NAME, t=cls.WINDOW_TITLE, s=False, mnb=False, mxb=False)
        main_layout = mc.formLayout(p=main_window)
        absolute_retiming_layout = mc.rowLayout(p=main_layout, nc=6)
        mc.formLayout(main_layout, e=True, af=(absolute_retiming_layout, 'top', 2))
        mc.formLayout(main_layout, e=True, af=(absolute_retiming_layout, 'left', 2))
        mc.formLayout(main_layout, e=True, af=(absolute_retiming_layout, 'right', 2))
        for i in range(1, 7):
            label = '{}'.format(i)
            cmd = partial(cls.retime, i, False)
            mc.button(p=absolute_retiming_layout, l=label, width=70, c=cmd)

        shift_left_layout = mc.rowLayout(p=main_layout, nc=2)
        mc.formLayout(main_layout, e=True, ac=(shift_left_layout, 'top', 2, absolute_retiming_layout))
        mc.formLayout(main_layout, e=True, af=(shift_left_layout, 'left', 2))
        mc.button(p=shift_left_layout, l='-2f', w=70, c=partial(cls.retime, -2, True))
        mc.button(p=shift_left_layout, l='-1f', w=70, c=partial(cls.retime, -1, True))

        shift_right_layout = mc.rowLayout(p=main_layout, nc=2)
        mc.formLayout(main_layout, e=True, ac=(shift_right_layout, 'top', 2, absolute_retiming_layout))
        mc.formLayout(main_layout, e=True, ac=(shift_right_layout, 'left', 28, shift_left_layout))
        mc.button(p=shift_right_layout, l='+1f', w=70, c=partial(cls.retime, 1, True))
        mc.button(p=shift_right_layout, l='+2f', w=70, c=partial(cls.retime, 2, True))

        move_to_next_cb = mc.checkBox(p=main_layout, l='move to next frame', v=False)
        mc.formLayout(main_layout, e=True, ac=(move_to_next_cb, 'top', 4, shift_left_layout))
        mc.formLayout(main_layout, e=True, af=(move_to_next_cb, 'left', 2))

        mc.showWindow()

    @classmethod
    def retime(cls, value, incremental, *args):
        move_to_next = False

        mc.undoInfo(ock=True)
        RetimingUtils.retime_keys(value, incremental, move_to_next)
        mc.undoInfo(cck=True)


if __name__ == "__main__":
    RetimeingUi.display()
