#!/usr/bin/perl 

#########################################################################
#                                                                       #
#       mv_files.perl: move a file, if it exists                        #
#                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                       #
#       last update: Nov 09, 2015                                       #
#                                                                       #
#########################################################################

$test = `ls -d *`;

if($test =~ /systemlog/){
    system("mv -f ./systemlog ./house_keeping/.");
}
if($test =~ /\.tl/){
    system("mv -f *.tl /data/mta/Script/Dumps/.");
}
