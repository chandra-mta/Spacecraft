#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Jan 31, 2019                                                   #
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

ifile = '/data/mta/Script/Dumps/gratstat.lis'
f     = open(ifile, 'r')
data  = [line.strip() for line in f.readlines()]
f.close()

bline  = '**********************************************************************\n'
line   = bline
name   = ''
for ent in data[1:]:
    mc = re.search('\*\*\*\*\*\*\*', ent)
    if mc is not None:
        line = line + bline
        if name != '':
            ofile = './Sub_html/' + str(name)
            fo    = open(ofile, 'w')
            fo.write(line)
            fo.close()

        line = bline
        name = ''
        continue
    else:
        mc2 = re.search('Move started at', ent)
        if mc2 is not None:
            atemp = re.split('Move started at', ent)
            btemp = re.split(';', atemp[1])
            #name  = float(btemp[0].strip())
            #name  = "%1.5f" % (round(name, 5))
            name = btemp[0].strip()
            
        line = line + ent + '\n'
