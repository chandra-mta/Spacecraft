#!/usr/bin/perl

#########################################################################
#                                                                       #
#   otg_cleanup.perl: check gratstat.lis exist and if so cat the        #
#                     result to main data file                          #
#                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                       #
#       last udpate: Nov 16, 2015                                       #
#                                                                       #
#########################################################################
 
$test = `ls *`;
if($test =~/gratstat.lis/){
    system("cat ./gratstat.lis >> /data/mta/Script/Dumps/gratstat.lis");
}

system("rm -f ./gratstat.in.tl  ./gratstat.lis ./otg-msids.list ./msids.list");

