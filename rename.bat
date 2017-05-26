@echo off
set xmldir=E:\work\dog\DDOG_CL\DDogCommon\UIEdit\res\ui_edit\xml
set out=的萨芬xx.html

if "%out%" == "" (python renameComps.py "%xmldir%") else (python renameComps.py -o "%out%" "%xmldir%") 
pause
