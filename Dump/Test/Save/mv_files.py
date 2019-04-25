#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#               mv_files.py: move *.tl files to Dump directory                              #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Feb 20, 2019                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import unittest

path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list_test'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(bin_dir)
#
#--- temp writing file name
#
rtail    = int(time.time()*random.random())
zspace   = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------------
#-- mv_files: move *.tl files to Dump directory                                               --
#-----------------------------------------------------------------------------------------------

def mv_files():
    """   
    move *.tl files to Dump directory
    """
#
#--- check systemlog is in working directory and if it does, move to <house_keeping>
#
    lfile = work_dir + 'systemlog'
    if os.path.isfile(lfile):
        cmd = 'mv -f ' + lfile + ' ' + work_dir + 'house_keeping/.'
        os.system(cmd)
#
#--- check tl files exist in working directory and if they do, move to dump directory
#
    cmd = 'ls -d ' + work_dir + '* > ' + zspace
    f   = open(zspace, 'r')
    out = f.read()
    f.close()
    cmd = 'rm -rf ' + zspace
    os.system(cmd)

    mc  = re.search('.tl', out)
    if mc is not None:
        cmd = 'mv -f *.tl ' + main_dir + '.'
        os.system(cmd)

#-----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    mv_files()
