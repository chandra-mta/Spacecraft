#!/usr/bin/env  /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#   update_rdb.py: update dataseeker rdb files for ccdm, pacd, mups, and elbi   #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Nov 10, 2015                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator
import math
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
#
#--- set a few directory paths
#
ds_dir        = '/data/mta/DataSeeker/data/repository/'
work_dir      = '/data/mta/Script/Dumps/'
script_dir    = work_dir   + 'Scripts/'
house_keeping = script_dir + 'house_keeping/'

#-----------------------------------------------------------------------------------
#-- run_rdb_updates: update dataseeker rdb files of ccdm, pacad, mups, and elbilow -
#-----------------------------------------------------------------------------------

def run_rdb_updates():
    """
    update dataseeker rdb files of ccdm, pacad, mups, and elbilow
    input:  none but read from the current trace log files
    output: updated rdb files of ccdm, pacad, mups, and elbilow
    """
#
#--- read the already processed data list
#
    file  = house_keeping + 'rdb_processed_list'
    f     = open(file, 'r')
    pdata = [line.strip() for line in f.readlines()]
    f.close()
#
#--- read the currently available data list
#
    cmd   = 'ls ' + work_dir + '/*.tl > ' + zspace
    os.system(cmd)
    f     = open(zspace, 'r')
    cdata = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)
#
#--- find new data
#
    ndata = list(set(cdata) - set(pdata))
#
#--- if there is no new data, exit
#
    if len(ndata) == 0:
        exit(1)
#
#--- make lists for ccdm, pcad, mups...
#--- also update already processed data list
#
    fo = open(file, 'w')
    fc = open('./ccdmlist',  'w')
    fp = open('./pcadlist',  'w')
    fm = open('./mupslist1', 'w')
    fn = open('./mupslist2', 'w')
    fe = open('./elbilist',  'w')
    for ent in ndata:
        fo.write(ent)
        fo.write('\n')
        if make_select_list(fc, ent, 'CCDM'):
            continue
        if make_select_list(fp, ent, 'PCAD'):
            continue
        if make_select_list(fm, ent, 'MUPSMUPS1'):
            continue
        if make_select_list(fn, ent, 'MUPSMUPS2'):
            continue
        if make_select_list(fe, ent, 'ELBILOW'):
            continue
    fo.close()
    fc.close()
    fp.close()
    fm.close()
    fe.close()
#
#--- run pcad  update
#
    cmd = script_dir + 'pcadfilter.pl -i @pcadlist -o ' + ds_dir + '/pcadfilter.rdb'
    try:
        os.system(cmd)
    except:
        print "PCAD extraction failed"
#
#--- run ccdm update
#
    cmd = script_dir + 'ccdmfilter.pl  -i @ccdmlist -o ' + ds_dir + '/ccdmfilter.rdb'
    try:
        os.system(cmd)
    except:
        print "CCDM extraction failed"
#
#--- run mups1 udpate; mups2 update will be done separately
#
    cmd  = script_dir + '/maverage.pl -i @mupslist1 -o mtemp1'
    cmd2 = 'cat mtemp1 >> ' + ds_dir + '/mups_1.rdb'
    try:
        os.system(cmd)
        os.system(cmd2)
    except:
        print "MUPS1 extraction failed"
#
#---- run elbi_low update
#
    cmd  = script_dir + '/maverage.pl -i @elbilist -o etemp'
    cmd2 = 'cat etemp >> ' + ds_dir + '/elbi_low.rdb'
    cmd3 = script_dir + '/filtersort2.pl ' + ds_dir + '/elbi_low.rdb'
    try:
        os.system(cmd)
        os.system(cmd2)
        os.system(cmd3)
    except:
        print "ELBI extraction failed"
#
#--- clean up 
#
    mcf.rm_file('./ccdmlist')
    mcf.rm_file('./pcadlist')
    mcf.rm_file('./mupslist1')
    mcf.rm_file('./mtemp1')
    mcf.rm_file('./elbilist')
    mcf.rm_file('./etemp')

#---------------------------------------------------------------------------
#-- run_mups2: extracting mups2 information for dataseeker rdb file      ---
#---------------------------------------------------------------------------

def run_mups2():
    """
    extracting mups2 information for dataseeker rdb file
    you need to run this separately from other process to run correctly

    input:  none but reads from the current trace log files
    output: updated dataseeker rdb file
    """
    cmd  = script_dir + '/maverage.pl -i @mupslist2 -o mtemp2'
    cmd2 = 'cat mtemp2 >> ' + ds_dir + '/mups_2.rdb'
    try:
        os.system(cmd)
        os.system(cmd2)
    except:
        print "MUPS2 extraction failed"
#
#--- clean up
#
    mcf.rm_file('./mupslist2')
    mcf.rm_file('./mtemp2')

#---------------------------------------------------------------------------
#-- make_select_list: write a line if the line contain "word"            ---
#---------------------------------------------------------------------------

def make_select_list(f, line, word):
    """
    write a line if the line contain "word"
    input:  f       --- file indicator
            line    --- a line to check and add
            word    --- a word to check whether it is in the line
    output: updated file
            return True/False
    """

    mc = re.search(word, line)
    if mc is not None:
        f.write(line)
        f.write('\n')

        return True
    else:
        return False 


#---------------------------------------------------------------------------

if __name__ == "__main__":

    run_rdb_updates()
#
#--- I do not know why, but mups2 extraction needs 
#--- to be run separately from others
#
    run_mups2()
