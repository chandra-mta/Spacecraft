#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       copy_tl_files_test.py: copy tl files for the test purpose                           #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Feb 12, 2019                                                   #
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
#-- copy_tl_files_test: copy *.tl files for test purpose                                    ----
#-----------------------------------------------------------------------------------------------

def copy_tl_files_test():
    """   
    this is a supplemental script for testing otg scripts; copying data for test processing
    """
#
#--- set the time limit: 24 hrs before the current
#
    t_limit = time.time() - 86400.0
#
#--- find any OTG related tl files exist in TLfiles directory
#
    cmd = 'ls /data/mta/Script/Dumps/TLfiles/*tl* > ' + zspace
    os.system(cmd)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    cmd = 'rm -f ' + zspace
    os.system(cmd)

    chk = 0
    for ent in data:
        mc = re.search('OTG', ent)
        if mc is None:
            continue

        out = os.path.getmtime(ent)
        if out > t_limit:
            cmd = 'cp ' + ent + ' ' + main_dir + '.'
            os.system(cmd)
            chk += 1


    if chk > 0:
        cmd = 'gzip -d ' + main_dir + '*.gz '
        os.system(cmd)

        line = 'OTG data found. Check: data/mta/Script/Dumps/Scripts/Test/mta_otg and \n'
        line = line + 'http://cxc.harvard.edu/mta_days//mta_otg/otg_test.html\n'
        fo   = open(zspace, 'w')
        fo.write(line)
        cmd  = 'cat ' + zspace + '| mailx -s "Subject: TEST---OTG data found"  tisobe@cfa.harvard.edu'
        os.system(cmd)

        cmd  = 'rm -f ' + zspace
        os.system(cmd)



#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    copy_tl_files_test()
