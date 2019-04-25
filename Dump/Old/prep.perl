#!/usr/bin/perl

#########################################################################################
#	                                            										#
#	prep.perl: prepare data for short time data	                        				#
#	    author: Takashi Isobe (tisobe@cfa.harvard.edu)                                  #
#	    Mar 14, 2000:	first version				                                    #
#       Oct 01, 2015:   modified for dea dumpdata extract                               #
#       Last update:    Oct 05, 2015                                                    #
#											                                            #
#########################################################################################

#
#--- set a couple of directory paths
#
$input_dir  = '/dsops/GOT/input/';
$script_dir = '/data/mta/Script/Dumps/Scripts/';
$repository = '/data/mta/DataSeeker/data/repository/';
#
#--- set environmental setting
#
$ENV{"ACISTOOLSDIR"}="/data/mta/Script/Dumps/Scripts";   #---- using lib/acisEng.ttm
#
#--- make back up before procceed
#
system("cp $repository/deahk_temp.rdb $repository/deahk_temp.rdb~");
system("cp $repository/deahk_elec.rdb $repository/deahk_elec.rdb~");
#
#--- read today's dump list
#
open(FH, "/data/mta/Script/Dumps/Scripts/house_keeping/today_dump_files");

while(<FH>) {
  chomp $_;
  $file = $_;
  $file = "$input_dir"."$file".'.gz';
#
#---- following is Peter Ford script to extract data from dump data
#
  `/bin/gzip -dc $file |$script_dir/getnrt -O  | $script_dir/deahk.pl`;

  `$script_dir/out2in.pl deahk_temp.tmp deahk_temp_in.tmp`;

  `$script_dir/average.pl -i deahk_temp_in.tmp -o deahk_temp.rdb`;

  `cat  deahk_temp.rdb >> $repository/deahk_temp.rdb`;

  `$script_dir/out2in.pl deahk_elec.tmp deahk_elec_in.tmp`;

  `$script_dir/average.pl -i deahk_elec_in.tmp -o deahk_elec.rdb`;

  `cat deahk_elec.rdb >> $repository/deahk_elec.rdb`;
   
   system('rm -rf deahk_*.tmp deahk_*.rdb ');

}
close(FH);
