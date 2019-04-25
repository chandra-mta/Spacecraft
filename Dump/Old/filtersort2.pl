#!/usr/bin/perl

if($#ARGV < 0)
{
    print "Usage: \n";
    print "\tfiltersort.pl <file>\n";

    exit (0);
}

my $inFile = $ARGV[0];
my $tmpFile = "${inFile}\.tmp";

my $comstr = "head -2 $inFile > $tmpFile";
system($comstr);
$comstr = "egrep '^[0-9]\\.[0-9]+e\\+07' $inFile | sort -u -n - >> $tmpFile";

system($comstr);
$comstr = "egrep '^[0-9]\\.[0-9]+e\\+08' $inFile | sort -u -n - >> $tmpFile";
system($comstr);
$comstr = "mv $tmpFile $inFile";
system($comstr);
