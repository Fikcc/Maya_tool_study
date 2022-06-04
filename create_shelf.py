import maya.cmds as mc

class SelfButton(object):
    def __init__(self, name):
        self.shelf_name = name
#        self.iconPath = iconPath
        
        self.labelBackground = (213, 169, 169, 0)
        self.labelColor = (220, 135, 206)
        
        self.cleanOldShalf()
        self.build()
        
    def cleanOldShalf(self):
        if mc.shelfLayout(self.shelf_name, ex = 1):
            if mc.shelfLayout(self.shelf_name, q = 1, ca = 1):
                for each in mc.shelfLayout(self.shelf_name, q = 1, ca = 1):
                    mc.deleteUI(each)
        
        else:
            mc.shelfLayout(self.shelf_name, p = 'ShelfLayout')
    
    def build(self):
        self.addButton('��ť1', command = 'print "1",', icon = 'ss.jpg')
        self.addButton('��ť2', icon = 'ss.jpg')
        p = mc.popupMenu(b = 1)
        self.addMenuItem(p, '�˵�1', icon = 'xiao.jpg')
        self.addMenuItem(p, '�˵�2', icon = 'xiao.jpg')
        sub = self.addSubMenu(p, '�Ӳ˵�1', icon = 'xiao.jpg')
        self.addMenuItem(sub, '�Ӳ˵�1��', icon = 'xiao.jpg')
        sub2 = self.addSubMenu(sub, '�Ӳ˵�2', icon = 'xiao.jpg')
        self.addMenuItem(sub2, '�Ӳ˵�2��1', icon = 'xiao.jpg')
        self.addMenuItem(sub2, '�Ӳ˵�2��2', icon = 'xiao.jpg')
        self.addMenuItem(sub, '�Ӳ˵�3' , icon = 'xiao.jpg')
        self.addMenuItem(p, '�˵�3', icon = 'xiao.jpg')
        self.addButton('��ť2', command = 'print "2",', icon = 'ss.jpg')
    
    def addButton(self, label, icon, command = '', doubleCommand = ''):
        """
        ֱ����shelf�������ɰ�ť�������ð�ť����ز���
        """
        mc.setParent(self.shelf_name)
        
        if icon:
#            icon = self.iconPath + icon
            mc.shelfButton(w = 37, h = 37, i = icon, l = label, c = command, dcc = doubleCommand, iol = label, olb = self.labelBackground, olc = self.labelColor)
    
    def addMenuItem(self, parent, label, icon, command = ''):
        """
        �ڰ�ť�����ʱִ�������Ӳ˵�����������ز���
        """
        if icon:
#            icon = self.iconPath + icon
            return mc.menuItem(p = parent, l = label, c = command, i = icon)
    
    def addSubMenu(self, parent, label, icon):
        """
        ΪmenuItem����Ӳ˵���ֻ��Ҫ�����丸������
        """
        if icon:
#            icon = self.iconPath + icon
            return mc.menuItem(p = parent, l = label, i = icon , sm = 1)

SelfButton('new_shelf')
