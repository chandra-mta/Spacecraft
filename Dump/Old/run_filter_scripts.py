#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       run_filter_scripts.py:  collect data and run otg and ccdm filter scripts            #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Jan 10, 2019                                                   #
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
import unittest

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"


mta_dir = '/data/mta/Script//Python_script2.7/'

sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

indir1   = '/dsops/GOT/'
indir2   = '/dsops/GOT/input/'
main_dir = '/data/mta/Script/Dumps/'

#-----------------------------------------------------------------------------------------------------------
#-- run_filter_script: collect data and run otg and ccdm filter scripts                                  ---
#-----------------------------------------------------------------------------------------------------------

def run_filter_script():
    """
    collect data and run otg and ccdm filter scripts
    input:  none
    outout: various *.tl files
    """

    unprocessed_data = copy_unprocessed_dump_em_files()

    if len(unprocessed_data) < 1:
        exit(1)

    filters_otg(unprocessed_data)
    filters_ccdm(unprocessed_data)
    filters_sim(unprocessed_data)

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
            #os.system(cmd)
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
            #os.system(cmd)
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
            #os.system(cmd)
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
    pfile = main_dir + 'Scripts/house_keeping/processed_list'
    f     = open(pfile, 'r')
    plist = [line.strip() for line in f.readlines()]
    f.close()

#---- UPDATE 10/15/18 ------
    if len(plist) < 1:
        chk = 1
    else:
#---- ADDED 03/23/16 END ------
        chk = 0
        last_entry = plist[len(plist)-1]
#
#--- read the all dump data located in /dsops/GOT/* sites
#
#    cmd = 'ls ' + indir1 + '* >  '+  zspace
#    os.system(cmd)
    cmd = 'ls ' + indir2 + '* > '+  zspace
    os.system(cmd)

    f     = open(zspace, 'r')
    flist = [line.strip() for line in f.readlines()]
    f.close()

    unprocessed_data = []

    cmd = 'mv ' + pfile + ' ' + pfile + '~'
    os.system(cmd)
    fo  = open(pfile, 'w')

    for ent in flist:
        mc  = re.search('Dump_EM_', ent)
        if mc is None:
            continue 
        mc2 = re.search('/dsops/GOT/', ent)
        if mc2 is None:
            continue

        line = ent + '\n'
        fo.write(line)

        if (not chk and ent == last_entry):
            chk = 1
            continue
        if chk == 1:
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

    fo.close()
#
#--- write out today dump data list
#
    outfile = main_dir + 'Scripts/house_keeping/today_dump_files'
    fo      = open(outfile, 'w')
    for ent in unprocessed_data:
        fo.write(ent)
        fo.write('\n')
    fo.close()

    return unprocessed_data


#-----------------------------------------------------------------------------------------------------------
 
if __name__ == "__main__":

    run_filter_script()
