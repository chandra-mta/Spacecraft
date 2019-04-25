#!/usr/bin/perl -w

#############################################################################################################
#                                                                                                           #
#               otg_proc.pl nd format otg tracelogs for input into gratstat.pl, cleano.pl                   #
#                                                                                                           #
#               author: B. Spitzbart (bspitzbart@cfa.harvard.edu)                                           #
#               modified by: T. Isobe (tisobe@cfa.harvard.edu)                                              #
#                                                                                                           #
#               Last update: Jun 09, 2015                                                                   #
#                                                                                                           #
#############################################################################################################

#
#--- set a few directories
#
my $tl_dir   = "/data/mta/Script/Dumps";                #---- where the data files are kelpt
my $work_dir = "/data/mta/Script/Dumps/Scripts/";       #---- where the computation is done
my $save_dir = "/data/mta/Script/Dumps/OTG/TLsave";     #---- the directory to save files with appropriate data

my $tmp_file = "$work_dir/gratstat.in.tl";
#
#--- if gratstat.in.tl already exists, append. otherwise create it.
#
my $fmt4 = 0;
if (-s $tmp_file) {
    open(TMP, ">>$tmp_file");
    $fmt4 = 1;
}
#
#--- open each data file and read data
#
foreach $file (<$tl_dir/*OTG*tl>) {
    my $save = 0;
    open TL, $file;
#
#--- keep column names in $hdr
#
    my $hdr  = <TL>;
    my $line = <TL>;

    while (defined ($line = <TL>)) {
#
#--- only data with "FMT4" are used
#
        if ($line =~ /FMT4/) {
            $save = 1;
#
#---  convert time to yyyydoy.hhmmss
#
            my $time = aform2dform(substr($line, 0, index($line, "\t")));
#
#--- reconstruct the line with the new time format
#
            $line    = sprintf "%16.8f %s", $time, substr($line, index($line, "\t"));

            if ($fmt4 > 0) {
                print TMP "$line";
            } else {
                open(TMP, ">>$tmp_file");
                print TMP "$hdr\n";
                print TMP "$line";
            }
            $fmt4 = 1;
        } else {
            if ($fmt4 > 0) {
                close TMP;
#
#----  sort, in case move spans two overlapping dumps
#
                system("head -1 $tmp_file > $tmp_file.tmp");
                system("tail -n +2 $tmp_file | sort -k 29,29 -u >> $tmp_file.tmp");
                system(" mv $tmp_file.tmp $tmp_file");
#
#---- run two perl script to complete the tasks
#
                system("$work_dir/gratstat.pl $tmp_file >> gratstat.lis");
                system("$work_dir/cleano.pl");
                unlink $tmp_file;
                open(TMP, ">>$tmp_file");
                $fmt4 = 0;
            }
        }
    }
#
#--- save the data file if it contains the data line with "FMT4" format
#
    if ($save > 0) {
       system("mv $file $save_dir");
    }
}
close TMP;

#----------------------------------------------------------------------------------------------------
#-- aform2dform: convert date form to yyyyddd.hh.mm.ss                                            ---
#----------------------------------------------------------------------------------------------------

sub aform2dform {

    ($line)    = @_;
#
#--- assume that time column is the first one and one before 'FMT4'
#
    @atemp     = split(/FMT4/, $line);
    $date_part = $atemp[0];
    $date_part =~s/^\s+|\s+$//g;
    @btemp     = split(/\s+/, $date_part);
    $year      = $btemp[0];
#
#--- year foramt could be 2014 or 14 to represent  year 2014
#
    if($year < 1900){
        if($year > 97){
            $year += 1900;
        }else{
            $year += 2000;
        }
    }
#
#--- ydate part
#
    $ydate = adjust_digit_len($btemp[1], 3);
#
#--- time part
#
    @ctemp = split(/$btemp[1]/, $date_part);
    $dtemp = $ctemp[1];
    $dtemp =~ s/^\s+|\s+$//g;
    @ftemp = split(/:/, $dtemp);
    $hh    = adjust_digit_len($ftemp[0], 2);
    $mm    = adjust_digit_len($ftemp[1], 2);
#
#--- round second part
#
    $ss    = sprintf("%.0f", $ftemp[2]);
    $ss    = int($ss);
    $ss    = adjust_digit_len($ss, 2);

    $date  = "$year"."$ydate".'.'."$hh"."$mm"."$ss";

    return $date
}

#----------------------------------------------------------------------------------------------------
#-- adjust_digit_len: padding with "0" in front of digit to adjust digit length                   ---
#----------------------------------------------------------------------------------------------------

sub adjust_digit_len{

    ( $val, $size) = @_;

    $val   =~ s/^\s+|\s+$//g;
    $start = length($val);
    for($i = $start; $i < $size; $i++){
        $val = '0'."$val";
    }
    return $val;
}


    
    
