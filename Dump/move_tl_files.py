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
#           last update: Feb 21, 2019                                                       #
#                                                                                           #
#############################################################################################

import sys
import os
import string
import re
import time
import Chandra.Time
import random

#
#--- reading directory list
#
#path = '/data/mta/Script/Python_script2.7/dir_list_py'
path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list'

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
sys.path.append(bin_dir)
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#-- convert factor to change time to start from 1.1.1998
#
tcorrect = (13.0 * 365.0 + 3.0) * 86400.0
#
#--- set directory paths
#
t_dir = main_dir + 'TLfiles/'
d_dir = main_dir + 'Dumps_mon/IN/'
s_dir = main_dir + 'Dumps_mon/Done/'

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
    today   = time.strftime("%Y:%j:%H:%M:%S" ,time.gmtime())
    today   = Chandra.Time.DateTime(today).secs
#
#--- set boundaries at 3 days ago and 6 days ago
#
    day3ago = today - 3 * 86400.0
    day6ago = today - 6 * 86400.0
#
#--- find trace log file older than 3 days in the main direcotry, remove them
#
    flist   = get_file_list(main_dir)

    remove_older_files(flist, day3ago)
#
#--- remove trace logs older than 6 days ago from TLfiles directory
#
    flist   = get_file_list(t_dir)

    remove_older_files(flist, day6ago)
#
#--- remove trace logs older than 6 days ago from Dumps_mon/IN/Done directory
#
    flist   = get_file_list(s_dir)

    remove_older_files(flist, day6ago)
#
#--- now copy new files to appropriate directory
#
    find_new_files(main_dir, d_dir, '*CCDM*')
    find_new_files(main_dir, d_dir, '*PCAD*')
    find_new_files(main_dir, d_dir, '*ACIS*')
    find_new_files(main_dir, d_dir, '*IRU*')
    find_new_files(main_dir, d_dir, '*MUPS2*')

    find_new_files(main_dir, t_dir, '*ELBILOW*', fzip=1)
    find_new_files(main_dir, t_dir, '*MUPS*',    fzip=1)

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

    cmd  = 'ls ' + dir_path + '/*  > '  + zspace
    os.system(cmd)

    f    = open(zspace, 'r')
    test = f.read(100000000)
    f.close()

    rm_file(zspace)

    htest = head.replace("*", "")

    chk  = 0
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

        out = read_data_file(zspace, remove=1)

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

    for ofile in flist:
        chk = find_time(ofile)

        if chk < cdate:
            rm_file(ofile)

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
    if dir2 == d_dir:
        slist1 = get_file_list(dir2,  head=head)
        slist2 = get_file_list(s_dir, head=head)
        slist  = slist1 + slist2
    else:
        slist  = get_file_list(dir2,  head=head)
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
    input:  none
    output: none.
    """

    cmd = 'ls -t  ' + save_dir + '*.tl* > ' +  zspace
    os.system(cmd)

    files = read_data_file(zspace, remove=1)

    dlen = len(files)
    if dlen > 100:
        for i in range (100, dlen):
            try:
                rm_file(files[i])

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
    output: <d_dir><category>list
    """

    cmd = 'ls ' + d_dir + '*CCDM*>'  + d_dir + 'ccdmlist'
    os.system(cmd)

    cmd = 'ls ' + d_dir + '*PCAD*>'  + d_dir + 'pcadlist'
    os.system(cmd)

    cmd = 'ls ' + d_dir + '*ACIS*>'  + d_dir + 'acislist'
    os.system(cmd)

    cmd = 'ls ' + d_dir + '*IRU*>'   + d_dir + 'irulist'
    os.system(cmd)

    cmd = 'ls ' + d_dir + '*MUPS2*>' + d_dir + 'mupslist'
    os.system(cmd)

#----------------------------------------------------------------------------
#-- read_data_file: read a data file and put into a data list              --
#----------------------------------------------------------------------------

def read_data_file(ifile, remove=0):
    """
    read a data file and put into a data list
    input:  ifile   --- data file name
            remove  --- if it is 1, delete the file after reading it
    output: data    --- a list of data
    """

    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        data = []

    if remove > 0:
        rm_file(ifile)

    return data

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def rm_file(ifile):

    if os.path.isfile(ifile):
        cmd = 'rm -f ' + ifile
        os.system(cmd)


#----------------------------------------------------------------------------

if __name__ == "__main__":

    move_tl_files()
    make_tl_list()
    clean_otg_tl()






