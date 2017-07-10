#!/usr/bin/env python
#  encoding=utf-8

import os
import sys
import shlex
import subprocess
import re
import tempfile
import argparse
import json
import xml.etree.ElementTree as ET

SVN = r"C:/Program Files/TortoiseSVN/bin/svn.exe"
TortoiseSVN = r"C:/Program Files/TortoiseSVN/bin/TortoiseProc.exe"
BComp = r"C:/Program Files/Beyond Compare 4/BComp.exe"

AUTHOR = None
REVISION = None
PATH_FROM = None
PATH_TO = None
PATH_FROM_NAME = None

# Index: arena/test.lua
# ===================================================================
# --- arena/test.lua  (revision 62120)
# +++ arena/test.lua  (revision 62121)
# @@ -63,7 +63,7 @@
P_ONEPATCH = r'Index:\s(.*)\r?\n={30,}\r?\n'

class Patch:
    """docstring for Patch"""
    __slots__ = ('path', 'content', 'revision', 'names')
    def __init__(self, content, revision):
        # self.path = arg[0]
        # self.names = arg[1]
        self.content = content
        self.revision = revision

# return (output, isOk)
def call(cmd, worddir = None, printOutput=False):
    # print("call %s" % cmd)
    output = None
    isOk = True
    if sys.platform == 'win32':
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)

    if printOutput:
        popen = subprocess.Popen(args, cwd = worddir)
        popen.wait()
        isOk = popen.returncode == 0
    else:
        popen = subprocess.Popen(args, cwd = worddir, stdout = subprocess.PIPE)
        outData, errorData = popen.communicate()
        if sys.version_info >= (3, 0):
            outData = str(outData, encoding = 'utf8')
        isOk = popen.returncode == 0
        output = outData if isOk else errorData
    return (output, isOk)

def getRevisions():
    cmd = '"%s" log -q -r %d:HEAD --xml --search %s' % (SVN, REVISION, AUTHOR)
    output, isOk = call(cmd, PATH_FROM)
    if not isOk:
        # print(output)
        raise Exception('svnerror', output)

    root = ET.fromstring(output)

    # print len(arr)
    revs = []
    for logentry in root.findall('logentry'):
        author = logentry.find('author').text
        if author == AUTHOR:
            revs.append(int(logentry.get('revision')))

    return revs

def createPatch(content, rev):
    # print(content)
    patch = Patch(content, rev)
    patch.names = re.findall(P_ONEPATCH, content)

    if sys.version_info >= (3, 0):
        content = content.encode(encoding = 'utf8')

    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(content)
    f.close()
    patch.path = f.name
    # print(f.name)

    return patch

def getPatchs(revisions):
    patchs = []
    for rev in revisions:
        output, isOk = call('"%s" diff -c %d' % (SVN, rev), PATH_FROM)
        if not isOk:
            raise Exception('svn diff', output)

        patchs.append(createPatch(output, rev))
    return patchs


def applyPatchs(patchs):
    for patch in patchs:
        output, isOk = call('"%s" patch %s' % (SVN, patch.path), PATH_TO)
        if not isOk:
            raise Exception('svn patch', output)
        else:
            print(output)

def openCampare(patchs):
    names = set()
    for patch in patchs:
        names.update(patch.names)
    filters = ';'.join(names)

    output, isOk = call('%s /iu  /filters="%s" %s %s' % (BComp, filters, PATH_FROM, PATH_TO))
    print(output)


def commitPatchs(patchs):
    revisions = ','.join([str(p.revision) for p in patchs])
    logmsg = "merge from %s %s" % (PATH_FROM_NAME, revisions)
    output, isOk = call('"%s" /command:commit /closeonend:0 /path:"%s" /logmsg:"%s"' % (TortoiseSVN, PATH_TO, logmsg))
    print(output, isOk)
    return isOk

def updateRepository(path):
    call('%s update "%s"' % (SVN, path), printOutput = True)

def readfile(filename):
    if not os.path.exists(filename):
        raise Exception('can not found file: %s' % filename)
    with open(filename) as f:
        data = f.read()
        f.close()
        return data

def writefile(filename, data):
    with open(filename, 'w') as f:
        f.write(data)
        f.close()

def readConfig(path, branch):
    global AUTHOR, PATH_FROM, PATH_TO, REVISION, PATH_FROM_NAME
    j = json.loads(readfile(path))
    AUTHOR = j['author']
    PATH_FROM_NAME = j['from']
    PATH_FROM = branch[j['from']]
    PATH_TO = branch[j['to']]
    REVISION = j['reversion']
    return j

def writeConfig(path, config):
    data = json.dumps(config, indent = 4)
    writefile(path, data)

# -------------- main ----------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='%(prog)s [options] config',
        description='merge svn from $from to $to')
    parser.add_argument('config', 
        help='config file')
    parser.add_argument('-b', '--branchs', default = 'branch.json',
        help='branchs config file(default: branch.json)')
    parser.add_argument('-o', '--origin',
        help='from branch')
    parser.add_argument('-t', '--to',
        help='to branch')
    parser.add_argument('-r', '--revs', nargs='*', type=int,
        help='reversion list')

    args = parser.parse_args()
    # print(args.config)
    

    branchs = dict();
    branchPath = args.branchs
    if not branchPath.endswith('.json'):
        branchPath = branchPath + '.json'
    branchs = json.loads(readfile(branchPath))

    configPath = os.path.abspath(args.config)
    if not configPath.endswith('.json'):
        configPath = configPath + '.json'
    config = readConfig(configPath, branchs)

    dontSave = False
    if args.origin is not None:
        if args.origin not in branchs:
            raise Exception('can not found origin branch' + origin)
        PATH_FROM = branchs[args.origin]
        PATH_FROM_NAME = args.origin
        dontSave = True

    if args.to is not None:
        if args.to not in branchs:
            raise Exception('can not found to branch' + to)
        PATH_TO = branchs[args.to]
        dontSave = True

    updateRepository(PATH_TO)

    revs = [] if args.revs is None else args.revs[:]
    if len(revs) > 0:
        revs.sort()
        dontSave = True
    else:
        revs = getRevisions()

    print(revs)
    if len(revs) == 0:
        print('have not new reversion')
    else:
        patchs = getPatchs(revs)
        applyPatchs(patchs)
        openCampare(patchs)
        if commitPatchs(patchs):
            lastReversion = revs[-1]
            config['reversion'] = lastReversion + 1
            config['lastReversion'] = lastReversion
            if not dontSave:
                writeConfig(configPath, config)

    # commitPatchs(None)
