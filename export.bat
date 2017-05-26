@echo off

set xmlDir=E:/work/dog/DDOG_CL/DDogCommon/UIEdit/res/ui_edit/xml
set backXmlDir=E:/work/dog/DDOG_CL/DDogCommon/UIEdit/res/ui_edit/xml2
set excelDir=E:/work/fox/tmp
set excelTemplate=E:/work/fox/template.xlsm
set out=E:/work/dog/DDOG_CL/DDogCommon/UIEdit/res/ui_edit/xml2/log.html

python exportxml.py  --xmlDir "%xmlDir%" --backXmlDir "%backXmlDir%" --excelDir "%excelDir%" --excelTemplate "%excelTemplate%" --out "%out%"
pause
