import maya.cmds as mc
import pymel.core as pm

def createMenu():
    if mc.menu(my_menu, ex = True):
        mc.deleteUI(my_menu)
    myWindow = pm.language.melGlobals['gMainWindow']
    my_menu = pm.menu(to = True, l = '~���Ȳ˵���~', p = myWindow)
    pm.menuItem(to = 1, p = my_menu, l = '�˵�1', c = 'print "�˵�һ"')
pmc.general.evalDeferred('createMenu()')
