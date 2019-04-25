#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       move_tl_files.py: manage # of trail files in the directories                        #
#                                                                                           #
#                   the file is kept in /data/mta/Script/Dumps/ for 3 days                  #
#                   after that the file is zipped and moved to TLfiles and kept another     #
#                   3 days. after that, the files will be deleted                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Mar 23, 2016                                                       #
#                                                                                           #
#############################################################################################

import sys
import os
import string
import re
import time
import random

#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#-- convert factor to change time to start from 1.1.1998
#
tcorrect = (13.0 * 365.0 + 3.0) * 3600.0 * 24.0
#
#--- set directory paths
#
mdir = '/data/mta/Script/Dumps/'
tdir = '/data/mta/Script/Dumps/TLfiles/'
ddir = '/data/mta/Script/Dumps/Dumps_mon/IN/'
#sdir = ddir + '/Done/'
sdir = '/data/mta/Script/Dumps/Dumps_mon/Done/'

#----------------------------------------------------------------------------
#-- move_tl_files: manage # of trail files in the directories              --
#----------------------------------------------------------------------------

def move_tl_files():
    """
    manage # of trace files in the directories
        the file is kept in /data/mta/Script/Dumps/ for 3 days
        and also gizpped files are save in two different directory
        after 3 days, the files are removed from the main directory, but
        other copies are kept another 6 days.

    input:  none but read from directories
    output: gzipped files in TLfiles/Dumps_mon/IN directories

    """
#
#--- find today's date in seconds from 1998.1.1
#
    today = int(tcnv.currentTime(format='SEC1998'))
#
#--- set boundaries at 3 days ago and 6 days ago
#
    day3ago = today - 3 * 86400
    day6ago = today - 6 * 86400
#
#--- find trace log file older than 3 days in the main direcotry, remove them
#
    flist = get_file_list(mdir)

    remove_older_files(flist, day3ago)
#
#--- remove trace logs older than 6 days ago from TLfiles directory
#
    flist = get_file_list(tdir)

    remove_older_files(flist, day6ago)
#
#--- remove trace logs older than 6 days ago from Dumps_mon/IN/Done directory
#
    flist = get_file_list(sdir)

    remove_older_files(flist, day6ago)
#
#--- now copy new files to appropriate directory
#
    find_new_files(mdir, ddir, '*CCDM*')
    find_new_files(mdir, ddir, '*PCAD*')
    find_new_files(mdir, ddir, '*ACIS*')
    find_new_files(mdir, ddir, '*IRU*')
    find_new_files(mdir, ddir, '*MUPS2*')

    #find_new_files(mdir, tdir, '*EPHIN*',   fzip=1)
    find_new_files(mdir, tdir, '*ELBILOW*', fzip=1)
    find_new_files(mdir, tdir, '*MUPS*',    fzip=1)

#----------------------------------------------------------------------------
#-- get_file_list: make a list of .tl* files in the given directory       ---
#----------------------------------------------------------------------------

def get_file_list(dir_path, head=''):
    """
    make a list of .tl* files in the given directory
    input:  dir_path    --- directory path
            head        --- head of the tl file. default: '*' (all tl files)
    output: out         --- a list of files
    """

    cmd = 'ls ' + dir_path + '/*  > '  + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    test = f.read(100000000)
    f.close()
    cmd = 'rm ' + zspace
    os.system(cmd)

    htest = head.replace("*", "")

    chk   = 0
    if htest== '':
        chk = 1
    else:
        mc = re.search(htest, test)
        if mc is not None:
            chk = 1

    mc = re.search('tl', test)

    if (mc is not None) and (chk > 0):
        cmd = 'ls ' + dir_path + '/' + head + '*.tl*  > '  + zspace
        os.system(cmd)
        f   = open(zspace, 'r')
        out = [line.strip() for line in f.readlines()]
        f.close()
    
        cmd = 'rm ' + zspace
        os.system(cmd)
    else:
        out = []
#
    return out

#----------------------------------------------------------------------------
#-- remove_older_files: remove files older than a give time                --
#----------------------------------------------------------------------------

def remove_older_files(flist, cdate):
    """
    remove files older than cdate
    input:  flist   --- a list of files
            cdate   --- a cut of date
    output: none 
    """

    for file in flist:
        chk = find_time(file)
        if chk < cdate:
            cmd = 'rm ' + file
            os.system(cmd)

#----------------------------------------------------------------------------
#-- find_new_files: find a new files in dir1 and make a copy of them in dir2 
#----------------------------------------------------------------------------

def find_new_files(dir1, dir2, head, fzip=0):
    """
    find a new files in dir1 and make a copy of them in dir2
    input:  dir1    --- the main directory
            dir2    --- the destination directory: we assume that files in 
                        this directory is already zipped
            head    --- head of the file name
            fzip    --- if 1 the files are zipped; default: 0 (no zip)
    output: copied and zipped files in dir2
    """
#
#--- find files names in dir1 and dir2. assume that dir2 save gipped files
#
    mlist = get_file_list(dir1, head=head)
#
#--- special treatment for Dumps_mon/IN/; files are kept in Done directory
#
    if dir2 == ddir:
        slist1 = get_file_list(dir2, head=head)
        slist2 = get_file_list(sdir, head=head)
        slist  = slist1 + slist2
    else:
        slist = get_file_list(dir2, head=head)
#
#--- remove "gz" from the file name and save it without the directory path
#
    tlist = []
    for ent in slist:
        out   = ent.replace('.gz', '')
        atemp = re.split('\/', out)
        tlist.append(atemp[-1])
#
#--- compare the file names from dir1 and dir2 and find new files in dir1
#
    nlist = []
    for ent in mlist:
        atemp = re.split('\/', ent)
        chk = 0
        for comp in tlist:
            if atemp[-1] == comp:
                chk = 1
                continue
        if chk == 0:
            nlist.append(ent)
#
#--- copy the new files to dir2 and gip it
#
    for ent in nlist:
        cmd = 'cp ' + ent + ' ' + dir2 + '/.'
        os.system(cmd)
#
#--- if zipping is asked, do so
#
    if fzip == 1:
        cmd = 'gzip ' + dir2 + '/*.tl > /dev/null'
        os.system(cmd)

#----------------------------------------------------------------------------
#-- find_time: convert trail log time system to seconds from 1998.1.1      --
#----------------------------------------------------------------------------

def find_time(file):
    """
    convert trail log time system to seconds from 1998.1.1
    input:  file name
    output: time in seconds from 1998.1.1
    """

    atemp = re.split('_', file)
    btemp = re.split('\.tl', atemp[-1])
    try:
        time = float(btemp[0]) - tcorrect
    except:
        time = 0.0

    return time

#----------------------------------------------------------------------------
#-- clean_otg_tl: cleaning up OTG TLsave directory                         --
#----------------------------------------------------------------------------

def clean_otg_tl():
    """
    cleaning up OTG TLsave directory
    input: none
    output: none.
    """

    cmd = 'ls -t /data/mta/Script/Dumps/OTG/TLsave/*.tl* > ' +  zspace
    os.system(cmd)

    f     = open(zspace, 'r')
    files = [line.strip() for line in f.readlines()]
    f.close()

    dlen = len(files)
    if dlen > 100:
        for i in range (100, dlen):
            try:
                cmd = 'rm ' + files[i]
                os.system(cmd)
            except:
                break

    if dlen > 50:
        for i in range (50, 100):
            try:
                if "gz" in file[i]:
                    continue
                else:
                    cmd = 'gzip  ' + files[i] + ' > /dev/null'
                    os.system(cmd)
            except:
                break


#----------------------------------------------------------------------------
#-- make_tl_list: make lists of the current tl files for each category    ---
#----------------------------------------------------------------------------

def make_tl_list():
    """
    make lists of the current tl files for each category
    input:  none but read from /data/mta/Script/Dumps/
    output: <adir>Dumps_mon/IN/<category>list
    """
    adir = '/data/mta/Script/Dumps/'

    cmd = 'ls ' + adir + '*CCDM*>'  + adir + 'Dumps_mon/IN/ccdmlist'
    os.system(cmd)

    cmd = 'ls ' + adir + '*PCAD*>'  + adir + 'Dumps_mon/IN/pcadlist'
    os.system(cmd)

    cmd = 'ls ' + adir + '*ACIS*>'  + adir + 'Dumps_mon/IN/acislist'
    os.system(cmd)

    cmd = 'ls ' + adir + '*IRU*>'   + adir + 'Dumps_mon/IN/irulist'
    os.system(cmd)

    cmd = 'ls ' + adir + '*MUPS2*>' + adir + 'Dumps_mon/IN/mupslist'
    os.system(cmd)


#----------------------------------------------------------------------------

if __name__ == "__main__":

    move_tl_files()
    make_tl_list()
    clean_otg_tl()






