#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#           ccdmfilter.py: filter the input PRIMARYCCDM file and convert the values         #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Feb 21, 2019                                                   #
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
import Chandra.Time
import unittest

path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list'
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

resolution = 300

#-----------------------------------------------------------------------------------------------
#-- ccdmfilter: filter the input PRIMARYCCDM file and convert the values                      --
#-----------------------------------------------------------------------------------------------

def ccdmfilter(infile, outfile=''):
    """
    filter the input PRIMARYCCDM file and convert the values to DataSeeker usable values
    input:  infile  --- a file name of the list of PRIMARYPCAD data
            outfile --- a output file name; if not given, <ds_dir>/ccdmfilter.rdb
    output: <ds_dir>/ccdmfilter.rdb
    """
#
#--- read input file names
#
    ccdmfiles = read_data_file(infile)

    if len(ccdmfiles) == 0:
        exit(1)
#
#--- default output file name
#
    if outfile == "":
        outfile = ds_dir + 'ccdmfilter.rdb'
#
#--- if there is no output file, create one
#
    if not os.path.isfile(outfile):
        hdr1 = 'time    CCSDSTMF    COBSRQID    COGEOMTR    SCIINS  3FAPOS  '
        hdr1 = hdr1 + '4HPOSARO    4LPOSARO    GRATING AOPCADMD    CORADMEN\n'
        hdr2 = 'N   S   N   S   S   N   N   N   S   S   S\n'

        fo   = open(outfile, 'w')
        fo.write(hdr1)
        fo.write(hdr2)
        fo.close()
        lasttime = 0.0
    else:
        data  = read_data_file(outfile)
        atemp = re.split('\s+', data[-1])
        try:
            lasttime = float(atemp[0])
        except:
            lasttime = 0.0
#
#--- append new data
#
    fo   = open(outfile, 'a')

    for cfile in ccdmfiles:
        try:
            data = read_data_file(cfile)
        except:
            continue

        hdr  = data[0]
        cols = re.split('\s+', hdr)
        data = data[2:]               #--- first two lines are headers
#
#--- convert the data set to a data list of each column
#
        d_dict = separate_data(data, cols)
        tlist  = d_dict['TIME']

        for k in range(0, len(tlist)):
#
#--- if the new data is in the "resolution", skip 
#
            if int(tlist[k]/ resolution) <= int(lasttime / resolution):
                continue
            else:
                lasttime = tlist[k]

            ctime = "%e" % (tlist[k] - (tlist[k] % resolution))
#
#---- find which instrument is used
#
            inst    =  find_instrument(d_dict['3TSCPOS'][k])
            grating = find_grating(d_dict['4HPOSBRO'][k], d_dict['4LPOSBRO'][k])

            line    = ctime + '\t'
            line    = line  + d_dict['CCSDSTMF'][k] + '\t'
            line    = line  + d_dict['COBSRQID'][k] + '\t'
            line    = line  + d_dict['COGEOMTR'][k] + '\t'
            line    = line  + inst                  + '\t'
            line    = line  + d_dict['3FAPOS'][k]   + '\t'
            line    = line  + d_dict['4HPOSARO'][k] + '\t'
            line    = line  + d_dict['4LPOSARO'][k] + '\t'
            line    = line  + grating               + '\t'
            line    = line  + d_dict['AOPCADMD'][k] + '\t'
            line    = line  + d_dict['CORADMEN'][k] + '\n'

            fo.write(line)

    fo.close()

#-----------------------------------------------------------------------------------------------
#-- separate_data: convert data into a list of each column                                   ---
#-----------------------------------------------------------------------------------------------

def separate_data(data, cols):
    """
    convert data into a list of each column
    input:  data    --- a list of data
            cols    --- col names
    output: d_dict  --- dictionary of data lists corresponding to col name
    """
    clen = len(cols)
    save = []
    for k in range(0, clen):
        save.append([])

    for ent in data:
        atemp = re.split('\t+', ent)
        if len(atemp) != clen:
            continue 

        ctime = convert_time_format(atemp[0])

        save[0].append(ctime)
        for k in range(1, clen):
            save[k].append(atemp[k])

    d_dict = {}
    for k in range(0, clen):
        d_dict[cols[k]] = save[k]

    return d_dict

#-----------------------------------------------------------------------------------------------
#-- convert_time_format: convert pcad time format to Chandra time: seconds from 1998.1.1      --
#-----------------------------------------------------------------------------------------------

def convert_time_format(line):
    """
    convert pcad time format to Chandra time: seconds from 1998.1.1
    input:  line    --- pcad time e.g.: 2019  42 14: 9:57.2
    output: ctime   --- chandra time
    """
    t    = line.strip()
    year = t[0] + t[1] + t[2] + t[3]

    yday = int(t[5] + t[6] + t[7])
    yday = adjust_digit_len(yday, 3)

    hh   = int(t[9] + t[10])
    hh   = adjust_digit_len(hh)

    mm   = int(t[12] + t[13])
    mm   = adjust_digit_len(mm)

    ss   = int(t[15] + t[16])
    ss   = adjust_digit_len(ss)
    ss   = ss  + t[17] +t[18]       #---- adjust_dgit_len takes only int; so add the dicimal part

    stime = year + ':' + yday + ':' + hh + ':' + mm + ':' + ss

    ctime = Chandra.Time.DateTime(stime).secs

    return ctime

#-----------------------------------------------------------------------------------------------
#-- adjust_digit_len: add leading '0' to fill the length of the value string                  --
#-----------------------------------------------------------------------------------------------

def adjust_digit_len(ss, digit=2):
    """
    add leading '0' to fill the length of the value string
    input:  ss  --- a numeric value (int or float. if float, dicimal part will be dropped)
    digit   --- length of the digit; default = 2
    output: lss --- adjust string
    """
#
#--- just in a case the numeric string comes with a leading '0', take int of that value
#--- to drop the leading zero. this also removes the decimal part
#
    try:
        iss  = int(float(ss))
        lss  = str(iss)
        slen = len(lss)
        for k in range(slen, digit):
            lss = '0' + lss
    except:
        lss  = str(ss)
    
    return lss

#-----------------------------------------------------------------------------------------------
#-- find_instrument:find which instrument is in the forcus from tscpos                        --
#-----------------------------------------------------------------------------------------------

def find_instrument(tscpos):
    """
    find which instrument is in the forcus from tscpos
    input:  tscpos  --- tscpos value
    output: inst    --- instrument
    """
    tscpos = float(tscpos)

    if (tscpos   >= 92703.0)   and (tscpos < 94103.0):
        inst = 'ACIS-I'

    elif (tscpos >= 74420.0)   and (tscpos < 76820.0):
        inst = 'ACIS-S'

    elif (tscpos >= -100800.0) and (tscpos < -98400.0):
        inst = 'HRC-S'

    elif (tscpos >= -51705.0)  and (tscpos < -49305.0):
        inst = 'HRC-I'

    else:
        inst = 'INDEF'

    return inst

#-----------------------------------------------------------------------------------------------
#-- find_grating: find grating                                                                --
#-----------------------------------------------------------------------------------------------

def find_grating(hposbro, lposbro):
    """
    find grating
    input:  hposbro --- 4HPOSBRO value
            lposbro --- 4LPOSBRO value
    output: grating --- grating
    """

    try:
        hposbro = float(hposbro)
        lposbro = float(lposbro)
    except:
        return 'NONE'

    if hposbro <= 20.0:
        grating = 'HETG'
        
    elif lposbro <= 20.0:
        grating = 'LETG'

    else:
        grating = 'NONE'

    return grating

#-----------------------------------------------------------------------------------------------
#-- read_data_file: read data file                                                            --
#-----------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):
    """
    read data file
    input:  ifile   --- data file name
            remove  --- if > 0: remove the file after reading
    output: data
    """

    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        data = []

    if remove > 0:
        cmd  = 'rm -f ' + ifile
        os.system(cmd)

    return data

#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        infile  = sys.argv[1].strip()
        outfile = ds_dir + 'ccdmfilter.rdb'

    elif len(sys.argv) == 3:
        infile  = sys.argv[1].strip()
        outfile = sys.argv[2].strip()

    else:
        print "Please give input file name"
        exit(1)

    ccdmfilter(infile, outfile)
