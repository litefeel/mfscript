#!/usr/bin/env python
#  encoding=utf-8
#  pip install openpyxl
#  pip install pyyaml

import os, os.path
import re
import argparse
from function import readfile, writefile, writeyaml

# <com.g2d.studio.ui.edit.gui.UELabel Attributes="" ImageFont="" clip_local_bounds="false" clipbounds="false" enable="true" enable_childs="true" height="30" local_bounds="0,0,60,30" lock="true" name="lb_title" text="动作" textBorderAlpha="0.0" textBorderColor="0" textColor="ffffffff" textFont="" textFontSize="20" text_anchor="C_C" text_offset_x="0" text_offset_y="0" uiAnchor="" uiEffect="" userData="" userTag="0" visible="true" visible_content="true" width="60" x="130.0" y="4.0" z="0.0"/>
# <com.g2d.studio.ui.edit.gui.UEButton Attributes="" ImageFont="" clip_local_bounds="false" clipbounds="false" enable="true" enable_childs="true" focusTextColor="ffffffff" height="35" imageAnchor="C_C" imageAtlasDown="" imageAtlasUp="" imageOffsetX="0" imageOffsetY="0" imageTextDown="" imageTextUp="" local_bounds="0,0,35,35" lock="true" name="btn_close" text="" textBorderAlpha="100.0" textBorderColor="ff000000" textDown="" textFont="" textSize="0" text_anchor="C_C" text_offset_x="0" text_offset_y="0" uiAnchor="" uiEffect="" unfocusTextColor="ffffffff" userData="" userTag="0" visible="true" visible_content="true" width="35" x="807.0" y="-3.0" z="0.0">
# <com.g2d.studio.ui.edit.gui.UEToggleButton Attributes="" ImageFont="" clip_local_bounds="false" clipbounds="false" enable="true" enable_childs="true" focusTextColor="ffffffff" height="78" imageAnchor="C_C" imageAtlasDown="#dynamic/associate/output/associate.xml|associate|9" imageAtlasUp="#dynamic/associate/output/associate.xml|associate|11" imageOffsetX="-15" imageOffsetY="0" imageTextDown="" imageTextUp="" isChecked="true" local_bounds="0,0,121,78" lock="true" name="tbt_an1" text="" textBorderAlpha="100.0" textBorderColor="ff000000" textDown="" textFont="" textSize="0" text_anchor="C_C" text_offset_x="0" text_offset_y="0" uiAnchor="" uiEffect="" unfocusTextColor="ffffffff" userData="" userTag="0" visible="true" visible_content="true" width="121" x="0.0" y="30.0" z="0.0">
# PATTERN = r'^(<com\.g2d\.studio\.ui\.edit\.gui\.(UELabel|UEButton|UEToggleButton) .*? name=")([^"]+)(" .*text=")([^"]+)(".*)$'
# P_BUTTON = r'^(<com\.g2d\.studio\.ui\.edit\.gui\.UEButton .*? name=")(btn_([^"]+))(" .*text=")([^"]+)(".*)$'
# P_TBUTTON = r'^(<com\.g2d\.studio\.ui\.edit\.gui\.UEToggleButton .*? name=")(tbt_([^"]+))(" .*text=")([^"]+)(".*)$'

COMPS_PREFIX = {
    "UELabel"        : "lb_",
    "UEButton"       : "btn_",
    "UEToggleButton" : "tbt_",
    "UECheckBox"     : "cb_",
    "UEImageBox"     : "ib_",
    "UETextInput"    : "ti_",
    "UETextBox"      : "tb_",
    "UETextBoxHtml"  : "tbh_",
    "UEGauge"        : "gg_",
    "UEScrollPan"    : "sp_",
    "UECanvas"       : "cvs_",
    "UEFileNode"     : "fn_",
    # "UETextInputMultiline": "tbt_",
}


arr = [r'^(<com\.g2d\.studio\.ui\.edit\.gui\.)(']
for k, v in COMPS_PREFIX.iteritems():
    arr.append(k)
    arr.append('|')
arr.pop()
arr.append(r')(.*? name=")([^"]+)(".*)$')
PATTERN = ''.join(arr)
# print('PATTERN', PATTERN)

# for k, v in COMPS_PREFIX.iteritems():
#     name = 'cs_'
#     ratio = difflib.SequenceMatcher(None, name, v).ratio()
#     print(v, name, ratio)

# return newname
def checkName(type, name):
    prefix = COMPS_PREFIX[type]
    if name[0:len(prefix)] == prefix:
        return name
    arr = name.split('_', 1)
    if len(arr) == 1:
        return prefix + name
    return prefix + arr[1]

def renameContent(data):
    pairMap = dict()
    def f(g):
        type = g.group(2)
        name = g.group(4)
        newname = checkName(type, name)
        if name == newname:
            return g.group(0)
        key = '%s;%s' % (name, newname)
        pair = pairMap.get(key, [name, newname, 0])
        pair[2] = pair[2] + 1
        pairMap[key] = pair
        return ''.join([g.group(1), type, g.group(3), newname, g.group(5)])
    return (re.sub(PATTERN, f, data, 0, re.M), pairMap)

def renameFile(baseDir, dir, name, errors):
    filename = os.path.join(dir, name)
    data = readfile(filename)
    newdata, pairMap = renameContent(data)
    writefile(filename, newdata)
    if len(pairMap) > 0:
        relname = os.path.relpath(filename, baseDir)
        errors.append((relname, pairMap.values()))

# baseDir 目录
# errors <(filename, [oldname, newname, count])>
def renameDir(baseDir, errors):
    for root, dirs, files in os.walk(baseDir):
        for f in files:
            if f.endswith('.gui.xml'):
                renameFile(baseDir, root, f, errors)


#-------------- main ----------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='%(prog)s [options] config',
        description='rename components name')
    parser.add_argument('xmldir', 
        help='xmldir')
    parser.add_argument('-o', '--out', 
        help='log file')

    args = parser.parse_args()
    errors = []
    xmldir = os.path.abspath(args.xmldir).decode('utf-8').encode('gb2312')
    logfile = args.out
    if logfile is not None:
        logfile = os.path.abspath(logfile).decode('utf-8').encode('gb2312')
    renameDir(xmldir, errors)

    if len(errors) > 0:
        from renderhtml import renderhtml
        renderhtml(errors, ("oldname", "newname", "count"), logfile)
