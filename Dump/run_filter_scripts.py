#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       run_filter_scripts.py:  collect data and run otg and ccdm filter scripts            #
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
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"
#
#--- read directory path
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
rtail  = int(time.time()* random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------------------------
#-- run_filter_script: collect data and run otg and ccdm filter scripts                                  ---
#-----------------------------------------------------------------------------------------------------------

def run_filter_script():
    """
    collect data and run otg and ccdm filter scripts
    input:  none, but read from /dsops/GOT/input/*Dump_EM*.gz
    outout: <working_dir>/*.tl files
    """
#
#--- find which dump data  are new
#
    unprocessed_data = copy_unprocessed_dump_em_files()

    if len(unprocessed_data) < 1:
        exit(1)
#
#--- prep for the filtering processes
#
    if os.path.isfile('./msids.list'):
        cmd = 'cp -f ' + house_keeping + 'msids.list .'
        os.system(cmd)

    if os.path.isfile('./otg-msids.list'):
        cmd = 'cp -f ' + house_keeping + 'otg-msids.list .'
        os.system(cmd)
#
#--- main processings
#
    filters_otg(unprocessed_data)
    filters_ccdm(unprocessed_data)
    filters_sim(unprocessed_data)
#
#--- remove the local copy of dump files
#
    for ent in unprocessed_data:
        cmd = 'rm -f ' + ent
        os.system(cmd)
#
#--- move *.tl files to working dir
#
    mv_files()

#-----------------------------------------------------------------------------------------------------------
#-- filters_otg: run acorn for otg filter                                                                ---
#-----------------------------------------------------------------------------------------------------------

def filters_otg(unprocessed_data):
    """
    run acorn for otg filter
    input:  unprocessed_data    --- list of data
    output: various *.tl files
    """

    for ent in unprocessed_data:
        cmd = "/usr/bin/env PERL5LIB='' "
        cmd = cmd + '/home/ascds/DS.release/bin/acorn -nOC otg-msids.list -f ' + ent
        try:
            bash(cmd, env=ascdsenv)
        except:
            pass

#-----------------------------------------------------------------------------------------------------------
#-- filters_ccdm: run acorn for ccdm filter                                                              ---
#-----------------------------------------------------------------------------------------------------------

def filters_ccdm(unprocessed_data):
    """
    run acorn for ccdm filter
    input: unprocessed_data    --- list of data
    output: various *.tl files
    """

    for ent in unprocessed_data:
        cmd = "/usr/bin/env PERL5LIB='' "
        cmd = cmd + '/home/ascds/DS.release/bin/acorn -nOC msids.list -f ' + ent
        try:
            bash(cmd, env=ascdsenv)
        except:
            pass

#-----------------------------------------------------------------------------------------------------------
#-- filters_sim: run acorn for sim filter                                                                 --
#-----------------------------------------------------------------------------------------------------------

def filters_sim(unprocessed_data):
    """
    run acorn for sim filter
    input: unprocessed_data    --- list of data
    output: various *.tl files
    """

    for ent in unprocessed_data:
        cmd = "/usr/bin/env PERL5LIB='' "
        cmd = cmd + '/home/ascds/DS.release/bin/acorn -nOC msids_sim.list -f ' + ent
        try:
            bash(cmd, env=ascdsenv)
        except:
            pass


#-----------------------------------------------------------------------------------------------------------
#-- copy_unprocessed_dump_em_files: collect unporcessed data and make a list                             ---
#-----------------------------------------------------------------------------------------------------------

def copy_unprocessed_dump_em_files():
    """
    collect unporcessed data and make a list
    input:  none, but copy data from /dsops/GOT/input/*Dump_EM_*
    output: unprocessed_data    ---- a list of data
            unzipped copies of the data in the current directoy
    """
#
#--- read the list of dump data already processed
#
    pfile = house_keeping + 'processed_list'
    plist = read_data_file(pfile)
#
#--- read the all dump data located in /dsops/GOT/input/ sites
#
    cmd = 'ls /dsops/GOT/input/*Dump_EM*gz > '+  zspace
    os.system(cmd)

    flist = read_data_file(zspace, remove=1)
#
#--- update processed data list file
#
    cmd = 'mv ' + pfile + ' ' + pfile + '~'
    os.system(cmd)
    fo  = open(pfile, 'w')

    for ent in flist:
        line = ent + '\n'
        fo.write(line)
    fo.close()
#
#--- find new entries
#
    try:
        new_data = numpy.setdiff1d(flist, plist)
    except:
        new_data = []

    unprocessed_data = []

    for ent in new_data:
        try:
            cmd = 'cp ' + ent + ' . '
            os.system(cmd)
            cmd = 'gzip -d *.gz'
            os.system(cmd)

            atemp = re.split('\/', ent)
            fname = atemp[-1]
            fname = fname.replace('.gz','')
            unprocessed_data.append(fname)
        except:
            pass
#
#--- write out today dump data list
#
    outfile = house_keeping + 'today_dump_files'
    fo      = open(outfile, 'w')
    for ent in unprocessed_data:
        fo.write(ent)
        fo.write('\n')
    fo.close()

    return unprocessed_data

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
        cmd = 'mv -f ' + lfile + ' '  + house_keeping + '.'
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
#-- read_data_file: read data file and create a data list                                    ---
#-----------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):
    """
    read data file and create a data list
    input:  ifile   --- input file name
            remove  --- if it is 1, remove the file after reading it
    output: data    --- a list of data
    """
    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        data = []

    if remove == 1:
        cmd = 'rm -f ' + ifile
        os.system(cmd)

    return data


#-----------------------------------------------------------------------------------------------------------
 
if __name__ == "__main__":

    run_filter_script()

