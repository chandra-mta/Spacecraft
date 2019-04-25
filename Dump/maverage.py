#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#               maverage.py: compute avg and std for tl data for a given resolution         #
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
#-- maverage: compute avg and std for tl data for a given resolution                         ---
#-----------------------------------------------------------------------------------------------

def maverage(infile, outfile):
    """
    compute avg and std for tl data for a given resolution
    input:  infile  --- a file name of the list of *.tl data
            outfile --- a output file name (no full path)
    output: <ds_dir>/outfile
    """
#
#--- add a path to DS directory
#
    outfile = ds_dir + outfile
#
#--- read input file names
#
    data_files = read_data_file(infile)

    if len(data_files) == 0:
        return 'NA'
#
#--- get column names
#
    out   = read_data_file(data_files[0])
    cols  = re.split('\s+', out[0])
    ncols = cols[1:]
    nlen  = len(ncols)
#
#--- if there is no output file, create one
#
    if not os.path.isfile(outfile):
        hline = 'time\tNavg'
        nline = 'N\tN'
        for k in range(1, len(cols)):
            aname = cols[k] + '_avg'
            sname = cols[k] + '_s'
            hline = hline + '\t' +  aname  + '\t' + sname
            nline = nline + '\t' +  'N'    + '\t' + 'N'

        hdr1  = hline + '\n'
        hdr2  = nline + '\n'

        fo   = open(outfile, 'w')
        fo.write(hdr1)
        fo.write(hdr2)
        fo.close()
        lastentry = 0.0
    else:
        data     = read_data_file(outfile)
        atemp    = re.split('\s+', data[-1])
        try:
            lastentry = float(atemp[0])
        except:
            lastentry = 0.0
#
#--- append new data
#
    fo   = open(outfile, 'a')

    save = []
    for k in range(0, nlen):
        save.append([])
    ncnt = 0

    lasttime = 0.0
    for cfile in data_files:
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

        if lasttime == 0.0:
            lasttime = tlist[0]

        for k in range(1, len(tlist)):
            if tlist[k] <= lastentry:
                lasttime = tlist[k]
                continue

            if tlist[k] - lasttime <= resolution:
                ncnt += 1

                for m in range(0, nlen):
                    save[m].append(d_dict[ncols[m]][k])
            else:
                atime = 0.5 * (lasttime + tlist[k])
                line  = "%8e\t%d" % (atime, ncnt)

                for m in  range(0, nlen):
                    avg = numpy.mean(save[m])
                    std = numpy.std(save[m])
                    line = line + "\t%.4f\t%.5f" % (avg, std)
                line = line + '\n'
                fo.write(line)
    
                for m in range(0, nlen):
                    save[m] =  [d_dict[ncols[m]][k]]
                    ncnt    = 1
                    lasttime = tlist[k]
#
#--- compute left over
#
    if ncnt > 0:
        atime = 0.5 * (lasttime + tlist[k])
        line  = "%8e\t%d" % (atime, ncnt)

        for k in  range(0, nlen):
            avg  = numpy.mean(save[k])
            std  = numpy.std(save[k])
            line = line + "\t%.4f\t%.5f" % (avg, std)

        line = line + '\n'
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
        chk = 0
        for k in range(1, clen):
            try:
                x = float(atemp[k])
            except:
                chk = 1
                break

        if chk > 0:
            continue

        ctime = convert_time_format(atemp[0])

        save[0].append(ctime)
        for k in range(1, clen):
            save[k].append(float(atemp[k]))

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

    hposbro = float(hposbro)
    lposbro = float(lposbro)

    if hposbro <= 20.0:
        grating = 'HETG'
        
    elif lposbro <= 20.0:
        grating = 'LETG'

    else:
        grating = 'NONE'

    return grating

#-----------------------------------------------------------------------------------------------
#-- filtersort: sort the data frame by one column with give col number                        --
#-----------------------------------------------------------------------------------------------

def filtersort(ifile, pos=0):
    """
    sort the data frame by one column with give col number
    input:  ifile   --- the data file
            pos     --- column position
    output: ifile   --- updated data file
    """

    data  = read_data_file(ifile)
    hdr1  = data[0]
    hdr2  = data[1]
    data  = data[2:]
    
    out   = sorted(data, key=lambda x : x[pos])

    ndata = [hdr1, hdr2] + out

    fo    = open(ifile, 'w')
    for ent in ndata:
        fo.write(ent)
        fo.write('\n')

    fo.close()

#-----------------------------------------------------------------------------------------------
#-- read_data_file: read data file                                                            --
#-----------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):

    try:
        f= open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        data = []

    if remove > 0:
        cmd = 'rm -f ' + ifile
        os.system(cmd)
    
    return data


#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 3:
        infile  = sys.argv[1].strip()
        outfile = sys.argv[2].strip()
    else:
        print "Please give input and output file names"
        exit(1)

    maverage(infile, outfile)
