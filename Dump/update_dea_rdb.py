#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#               update_dea_rdb.py: update DS deahk realated rdb files                       #
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
import subprocess
import Chandra.Time
import unittest
#
#--- set environment for "getnrt"
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"
ascdsenv['ACISTOOLSDIR'] = "/data/mta/Script/Dumps/Scripts"

#
#--- read directory list
#
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
#
#NOTE: this is a replacement for the old perl scripts: out2in.pl average.pl prep.perl
#
#-----------------------------------------------------------------------------------------------
#-- update_dea_rdb: update DS deahk realated rdb files                                        --
#-----------------------------------------------------------------------------------------------

def update_dea_rdb():
    """
    update DS deahk realated rdb files
    input:  none but read from: <house_keeping>/today_dump_files
    output: <ds_dir>/deahk_temp <ds_dir>/deahk_elec
    """
#
#--- make backup first
#
    cmd = 'cp ' + ds_dir + 'deahk_temp.rdb ' + ds_dir + 'deahk_temp.rdb~'
    os.system(cmd)
    cmd = 'cp ' + ds_dir + 'deahk_elec.rdb ' + ds_dir + 'deahk_elec.rdb~'
    os.system(cmd)
#
#--- read today's dump list
#
    dfile = house_keeping + 'today_dump_files'
    data  = read_data_file(dfile)

    for ent in data:
        ifile = '/dsops/GOT/input/' + ent + '.gz'
#
#--- run Peter Ford's scripts and pipe into deakh.py
#
        cmd1  = "/usr/bin/env PERL5LIB='' "
        #cmd2  = '/bin/gzip -dc ' + ifile +  '|' + bin_dir + 'getnrt -O | ' + bin_dir + 'deahk.py'
        cmd2  = '/bin/gzip -dc ' + ifile +  '|' + bin_dir + 'getnrt -O | ' + bin_dir + 'deahk.pl'
        cmd   = cmd1 + cmd2 
        bash(cmd, env=ascdsenv)

    if os.path.isfile('./deahk_temp.tmp'):
        process_deahk('deahk_temp')

    if os.path.isfile('./deahk_elec.tmp'):
        process_deahk('deahk_elec')

#-----------------------------------------------------------------------------------------------
#-- process_deahk: process deahk data to match dataseeker data format                         --
#-----------------------------------------------------------------------------------------------

def process_deahk(dtype):
    """
    process deahk data to match dataseeker data format
    input: dtype    --- data type; either deahk_temp or deahk_elec
            we assume that  the input file name is ./<dtype>.tmp
    output: <ds_dir>/<dtype>.rdb
    """
#
#--- we assume that input data file is in the current direcotry with sufix of ".tmp"
#
    ifile = dtype + '.tmp'
    rdb   = ds_dir + dtype + '.rdb'

    data  = read_data_file(ifile, remove=1)
#
#--- convert time in seconds from 1998.1.1
#
    cdata = convert_time_format(data)
#
#--- take time average of <resolution>
#
    rdata = time_average(cdata)
#
#--- update the rdb file
#
    fo    = open(rdb, 'a')
    for ent in rdata:
        fo.write(ent)
        fo.write('\n')
    fo.close()


#-----------------------------------------------------------------------------------------------
#-- convert_time_format: convert time format from <yyyy>:<ddd>:<hh>:<mm>:<ss> to Chandra time --
#-----------------------------------------------------------------------------------------------

def convert_time_format(data):
    """
    convert time format from <ddd>:<seconds> to Chandra time
    we assume that the first entry of the list is the time 
    input:  data    --- a list of data
    output: save    --- a list of lists of data with converted time foramt
    """
#
#--- find today's year and ydate
#
    out   = time.strftime("%Y:%j", time.gmtime())
    atemp = re.split(':', out)
    year  = atemp[0]
    yday  = atemp[1]
    save  = []
    for ent in data:
        atemp = re.split('\s+', ent)
        date  = atemp[1]
        btemp = re.split(':', date)
        ydate = int(btemp[0])
        ytime = float(btemp[1])
        uyear = year
#
#--- if today's ydate is the first part of the year, it could be possible that the date is from the last year;
#--- make sure tat the correspoinding year is a correct one.
#
        if yday < 10:
            if ydate > 350:
                uyear = year -1
        sydate = adjust_digit(ydate, digit=3)

        ytime /= 86400.0
        hp     = ytime * 24
        hh     = int(hp)
        lhh    = adjust_digit(hh)
        mp     = (hp - hh) *   60
        mm     = int(mp)
        lmm    = adjust_digit(mm)
        ss     = int((mp - mm) * 60)
        lss    = adjust_digit(ss)

        stime  = str(uyear) + ':' + str(sydate) + ':' + str(lhh) + ':' + str(lmm) + ':' + str(lss)

        try:
            ctime = Chandra.Time.DateTime(stime).secs
        except:
            continue

        out = ent.replace(date, str(ctime))
        save.append(out)

    return save

#-----------------------------------------------------------------------------------------------
#-- adjust_digit: add leading zero to adjust the length of print out numerical string         --
#-----------------------------------------------------------------------------------------------

def adjust_digit(aa, digit=2):
    """
    add leading zero to adjust the length of print out numerical string
    input: aa   --- a nemerical value
    outout: aa  --- adjusted numerical value in string
    """

    iaa  = int(aa)
    aa   = str(iaa)
    alen = len(aa)
    for k in range(alen, digit):
        aa = '0' + aa

    return aa

#-----------------------------------------------------------------------------------------------
#-- time_average: compute avg and std for the data for a given resolution                     --
#-----------------------------------------------------------------------------------------------

def time_average(data):
    """
    compute avg and std for the data for a given resolution
    input:  data    --- a list of column data lists
    output: mdata   --- a list of data
    """
    cdata = convert_to_col_data(data)
    clen  = len(cdata)
    dlen  = len(cdata[1])

    save  = []
    for k in range(0, clen):
#
#--- time is kept in the second column
#
        save.append([])
    t_list = cdata[1]
    tlast  = t_list[0]

    mdata  = []
    for m in range(0, dlen):
        if t_list[m] - tlast <= resolution:
            for k in range(0, clen):
                save[k].append(cdata[k][m])

        else:
            atime = numpy.mean(save[1])
            ncnt  = len(save[1])
            line  = "%10e\t%d" % (atime, ncnt)
#
#--- dea data starts from third column
#
            for k in range(2, clen):
                avg = numpy.mean(save[k])
                std = numpy.std(save[k])
                line = line + "\t%.4f\t%.5f" % (avg, std)
            line = line + '\n'
            mdata.append(line)

            for k in range(0, clen):
                save[k] = [cdata[k][m]]
                tlast   = t_list[m]
#
#--- compute left over
#
    if len(save[1]) > 0:
        atime = numpy.mean(save[1])
        ncnt  = len(save[1])
        line  = "%8e\t%d" % (atime, ncnt)
        for k in range(2, clen):
            avg = numpy.mean(save[k])
            std = numpy.std(save[k])
            line = line + "\t%.4f\t%.5f" % (avg, std)
        line = line + '\n'
        mdata.append(line)

    return mdata

#-----------------------------------------------------------------------------------------------
#-- convert_to_col_data: convert a list of data line into a list of column data lists         --
#-----------------------------------------------------------------------------------------------

def convert_to_col_data(data):
    """
    convert a list of data line into a list of column data lists
    input:  data    --- a list of data lines
    output: save    --- a list of column data lists
    """

    atemp = re.split('\s+', data[0])
    dlen  = len(atemp)

    save  = []
    for k in range(0, dlen):
        save.append([])

    for ent in data:
        atemp = re.split('\s+', ent)
        for k in range(0, dlen):
            try:
                save[k].append(float(atemp[k]))
            except:
                save[k].append(atemp[k])

    return save

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
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def rm_file(ifile):

    if os.path.isfile(ifile):
        cmd = 'rm -f ' + ifile
        os.system(cmd)

#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_dea_rdb()

