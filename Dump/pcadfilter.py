#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#           pcadfilter.py: filter the input PRIMARYPCAD file and convert the values         #
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
rad_p_deg  = math.pi /180.0

#-----------------------------------------------------------------------------------------------
#-- pcadfilter: ilter the input PRIMARYPCAD file and convert the values                       --
#-----------------------------------------------------------------------------------------------

def pcadfilter(infile, outfile=''):
    """
    filter the input PRIMARYPCAD file and convert the values to DataSeeker usable values
    input:  infile  --- a file name of the list of PRIMARYPCAD data
            outfile --- a output file name; if not given, <ds_dir>/pcadfilter.rdb
    output: <ds_dir>/pcadfilter.rdb
    """
#
#--- read input file names
#
    pcadfiles = read_data_file(infile)

    if len(pcadfiles) == 0:
        exit(1)
#
#--- default output file name
#
    if outfile == "":
        outfile = ds_dir + 'pcadfilter.rdb'
#
#--- if there is no output file, create one
#
    if not os.path.isfile(outfile):
        hdr1 = 'time    AOATTRAS    AOATTDEC    AOATTROL\n'
        hdr2 = 'N   N   N   N\n'
        fo   = open(outfile, 'w')
        fo.write(hdr1)
        fo.write(hdr2)
        fo.close()
        lasttime = 0.0
    else:
        data     = read_data_file(outfile)
        atemp    = re.split('\s+', data[-1])
        try:
            lasttime = float(atemp[0])
        except:
            lasttime = 0.0
#
#--- append new data
#
    fo   = open(outfile, 'a')

    for pfile in pcadfiles:
        try:
            data = read_data_file(pfile)
        except:
            continue

        hdr  = data[0]
        cols = re.split('\s+', hdr)
        data = data[2:]               #--- first two lines are headers
#
#--- convert the data set to a data list of each column
#
        [tlist,tqt1, tqt2, tqt3, tqt4, hen] = separate_data(data, cols)

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
#--- convert quat values to euler ra/dec/roll
#
            [ra, dec, roll] = quat_to_euler(tqt1[k], tqt2[k], tqt3[k], tqt4[k])
            ra    = "%e" % ra
            dec   = "%e" % dec
            roll  = "%e" % roll

            line  = ctime + '\t' + ra + '\t' + dec + '\t' + roll + '\n'
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
    output: save    --- a list of lists of data 
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
        save[1].append(float(atemp[1]))
        save[2].append(float(atemp[2]))
        save[3].append(float(atemp[3]))
        save[4].append(float(atemp[4]))

    return save

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
#-- quat_to_euler: convert quat values into ra/dec/roll                                       --
#-----------------------------------------------------------------------------------------------

def quat_to_euler(q1, q2, q3, q4):
    """
    convert quat values into ra/dec/roll
    input:  q1/q2/q3/q4 ---- quat values
    output: ra/dec/roll
    """
    q12  = 2.0 * q1 * q1
    q22  = 2.0 * q2 * q2
    q32  = 2.0 * q3 * q3

    en00 = 1.0 - q22 - q32 
    en01 = 2.0 * (q1 * q2 + q3 * q4) 
    en02 = 2.0 * (q3 * q1 - q2 * q4)

    en10 = 2.0 * (q1 * q2 - q3 * q4) 
    en11 = 1.0 - q32 - q12  
    en12 = 2.0 * (q2 * q3 + q4 * q1)

    en20 = 2.0 * (q3 * q1 + q2 * q4) 
    en21 = 2.0 * (q2 * q3 - q1 * q4) 
    en22 = 1.0 - q12 - q22

    ra   = math.atan2(en01, en00)

    dec  = math.atan2(en02, math.sqrt(en00 * en00 + en01 * en01))

    ent1 =  en20 * math.sin(ra) - en21 * math.cos(ra)
    ent2 = -en10 * math.sin(ra) + en11 * math.cos(ra)
    roll = math.atan2(ent1, ent2)

    ra   /= rad_p_deg
    dec  /= rad_p_deg
    roll /= rad_p_deg

    if ra < 0.0:
        ra   += 360.0

    if roll < -1.0e-13:
        roll += 360.0

    if dec < -90.0 or dec > 90.0:
        print "Something wrong with dec:  " + str(dec)

    return [ra, dec, roll]

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
        outfile = ds_dir + 'pcadfilter.rdb'

    elif len(sys.argv) == 3:
        infile  = sys.argv[1].strip()
        outfile = sys.argv[2].strip()

    else:
        print "Please give input file name"
        exit(1)

    pcadfilter(infile, outfile)
