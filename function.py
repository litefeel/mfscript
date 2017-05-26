#!/usr/bin/env python
#  encoding=utf-8

import os.path
import shutil

def makebasename(filename):
    dir = os.path.dirname(filename)
    if len(dir) > 0 and not os.path.exists(dir):
        os.makedirs(dir)

def readfile(filename, mode = 'r'):
    if not os.path.exists(filename):
        raise Exception('can not found file: %s' % filename)
    with open(filename, mode) as f:
        data = f.read()
        f.close()
        return data

def writefile(filename, data, mode = 'w'):
    makebasename(filename)
    with open(filename, mode) as f:
        f.write(data)
        f.close()

def copyfile(origin, to):
    makebasename(to)
    shutil.copyfile(origin, to)

def writeyaml(data, filename):
    import yaml
    s = yaml.dump(data)
    writefile(filename, s)

def readyaml(filename):
    data = readfile(filename)
    import yaml
    return yaml.load(data)

