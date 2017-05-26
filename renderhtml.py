#!/usr/bin/env python
#  encoding=utf-8
#  pip install openpyxl

import os, os.path
import webbrowser
import tempfile
from function import readfile, writefile

def addHead(htmls, filename):
    htmls.append('<hr/><h4>%s</h4>' % filename)

def addTableHead(htmls):
    htmls.append('<table>')

def addTableRaw(htmls, names):
        htmls.append('<tr>')
        for name in names:
            htmls.append('<th align="left" width="200px">%s</th>' % name)
        htmls.append('</tr>')

def addTableTail(htmls):
    htmls.append('</table>')

def addTable(htmls, list):
    addTableHead(htmls)
    for s in list:
        addTableRaw(htmls, s)
    addTableTail(htmls)

def printHtml(errors, config):
    htmls = ['<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body>\n\n']
    for arr in errors:
        addTableHead(htmls, os.path.relpath(arr[0], config.xmlDir))
        keys = arr[1]
        for k in sorted(keys.keys()):
            htmls.append('<tr><th align="left" width="200px">%s</th><th>%d</th></tr>' % (k, keys.get(k)))
        keys = arr[2]
        for k in sorted(keys.keys()):
            htmls.append('<tr><th align="left" width="200px"><font color="red">%s</font></th><th>%d</th></tr>' % (k, keys.get(k)))
        addTableTail(htmls)
    htmls.append('</body></html>')
    writefile(config.log, '\n'.join(htmls))
    webbrowser.open(config.log)



# errors <(filename, <[oldname, newname, count]>)>
# tableTitles (...)
def renderhtml(errors, tableTitles, htmlfile):
    htmls = ['<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body>\n\n']
    for arr in errors:
        addHead(htmls, arr[0])
        addTable(htmls, arr[1])
    htmls.append('</body></html>')

    if htmlfile is None or len(htmlfile) == 0:
        f = tempfile.NamedTemporaryFile(suffix = '.html', delete=False)
        htmlfile = f.name

    writefile(htmlfile, ''.join(htmls))
    webbrowser.open(htmlfile)



