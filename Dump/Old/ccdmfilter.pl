#!/usr/bin/perl

#------------------------------------------------------------------------------
#
# ccdmfilter.pl  This program is used to filter the input PRIMARYCCDM file
#                and convert the values to DataSeeker usable values
#                This final output is either appended to a new file or
#                a new table is created depending on whether or not
#                <outfile> exists
#                It also only samples the input file at <resolution> sec 
#                intervals
#
#       b. spitzbart (bspitzbart@cfa.harvard.edu)
#
#       modified by t. isobe (tisobe@cfa.harvard.edu)
#       last updatd: Nov10, 2015
#
#------------------------------------------------------------------------------

$verbose    = 0;
$infile;
$outfile;
$resolution = 300;
#
#--- Parse input arguments
#
&parse_args;

if ($verbose >= 2) {
    print "$0 args:\n";
    print "\tinfile:\t\t$infile\n";
    print "\toutfile:\t\t$outfile\n";
    print "\tresolution:\t\t$resolution\n";
    print "\tverbose:\t\t$verbose\n";
}  

my @ccdmfiles;
my $ccdmfile;
my $counter;


if ($infile =~ /^\@/) {
    $infile = substr($infile, 1);

    my @patharr = split("/", $infile);
    my $path = "";
    
    for ($ii = 0; $ii < $#patharr; $ii++) {
	    $path .= "/$patharr[$ii]";
    }

    open infile;
    
    $counter = 0;
    while($ccdmfile = <infile>) {
	    chomp $ccdmfile;
	    $ccdmfiles[$counter++] = $path . $ccdmfile;
    }

} else {
    $ccdmfiles[0] = $infile;
}

my $hdr;
my @hdrline;
my $intimecol = 0;
#
#--- CCDM columns
#
my $inccsdstmfcol  = 0;
my $incobsrqidcol  = 0;
my $incogeomtrcol  = 0;
my $in3tscposcol   = 0;
my $in3faposcol    = 0;
my $in4hposarocol  = 0;
my $in4lposarocol  = 0;
my $in4hposbrocol  = 0;
my $in4lposbrocol  = 0;
my $inaopcadmdcol  = 0;
my $incoradmencol  = 0;
#
#--- Get column information on the output PRIMARYCCDM file
#--- CCDM columns
#
my $outccsdstmfcol = 0;
my $outcobsrqidcol = 0;
my $outcogeomtrcol = 0;
my $outsciinscol   = 0;
my $out3faposcol   = 0;
my $out4hposarocol = 0;
my $out4lposarocol = 0;
my $outgratingcol  = 0;
my $outaopcadmdcol = 0;
my $outcoradmencol = 0;
my $outtimecol     = 0;

if (-e $outfile) {
    open OUTFILE, "<$outfile" or die;

    $hdr = <OUTFILE>;
    
    chomp $hdr;
    @hdrline = split("\t", $hdr);

    for ($ii=0; $ii<=$#hdrline; $ii++) {
	    if ($hdrline[$ii] eq "time" || $hdrline[$ii] eq "TIME") {
	        $outtimecol = $ii;

	    } elsif ($hdrline[$ii] eq "CCSDSTMF") {
	        $outccsdstmfcol = $ii;

	    } elsif ($hdrline[$ii] eq "COBSRQID") {
	        $outcobsrqidcol = $ii;

	    } elsif ($hdrline[$ii] eq "COGEOMTR") {
	        $outcogeomtrcol = $ii;

	    } elsif ($hdrline[$ii] eq "3FAPOS") {
	        $out3faposcol = $ii;

	    } elsif ($hdrline[$ii] eq "4HPOSARO") {
	        $out4hposarocol = $ii;

	    } elsif ($hdrline[$ii] eq "4LPOSARO") {
	        $out4lposarocol = $ii;

	    } elsif ($hdrline[$ii] eq "GRATING") {
	        $outgratingcol = $ii;

	    } elsif ($hdrline[$ii] eq "SCIINS") {
	        $outsciinscol = $ii;

	    } elsif ($hdrline[$ii] eq "AOPCADMD") {
	        $outaopcadmdcol = $ii;

	    } elsif ($hdrline[$ii] eq "CORADMEN") {
	        $outcoradmencol = $ii;
	    }
    } # for ($ii=0; $ii<=$#hdrline; $ii++)

    close OUTFILE;

    open OUTFILE, ">>$outfile";

} else {
    $outtimecol = 0;
    $outccsdstmfcol = 1;
    $outcobsrqidcol = 2;
    $outcogeomtrcol = 3;
    $outsciinscol   = 4;
    $out3faposcol   = 5;
    $out4hposarocol = 6;
    $out4lposarocol = 7;
    $outgratingcol  = 8;
    $outaopcadmdcol = 9;
    $outcoradmencol = 10;

    @hdrline = (
		"time",
		"CCSDSTMF",
		"COBSRQID",
		"COGEOMTR",
		"SCIINS",
		"3FAPOS",
		"4HPOSARO",
		"4LPOSARO",
		"GRATING",
		"AOPCADMD",
		"CORADMEN",
		);

    open OUTFILE, ">$outfile";
    $hdr = join ("\t", @hdrline);
    
    print OUTFILE $hdr;
    print OUTFILE "\n";

    my @rdbTypeArr = ('N',
		      'S',
		      'N',
		      'S',
		      'S',
		      'N',
		      'N',
		      'N',
		      'S',
		      'S',
		      'S');

    my $rdbTypeLine = join("\t", @rdbTypeArr);
    print OUTFILE $rdbTypeLine;
    print OUTFILE "\n";
}

foreach $file (@ccdmfiles) {

    open ccdmfile, "$file" or die;

    $hdr = <ccdmfile>;
    chomp $hdr;
#
#--- Get column information on the input PRIMARYCCDM file
#
    @hdrline = split ("\t", $hdr);
    $intimecol = 0;
#
#--- CCDM columns
#
    $inccsdstmfcol = 0;
    $incobsrqidcol = 0;
    $incogeomtrcol = 0;
    $in3tscposcol  = 0;
    $in3faposcol   = 0;
    $in4hposarocol = 0;
    $in4lposarocol = 0;
    $in4hposbrocol = 0;
    $in4lposbrocol = 0;
    $inaopcadmdcol = 0;
    $incoradmencol = 0;

    for ($ii=0; $ii<=$#hdrline; $ii++) {
	    if ($hdrline[$ii] eq "TIME" || $hdrline[$ii] eq "time") {
	        $intimecol = $ii;

	    }elsif ($hdrline[$ii] eq "CCSDSTMF") {
	        $inccsdstmfcol = $ii;

	    }elsif ($hdrline[$ii] eq "COBSRQID") {
	        $incobsrqidcol = $ii;

	    }elsif ($hdrline[$ii] eq "COGEOMTR") {
	        $incogeomtrcol = $ii;

	    }elsif ($hdrline[$ii] eq "3FAPOS") {
	        $in3faposcol = $ii;

	    }elsif ($hdrline[$ii] eq "3TSCPOS") {
	        $in3tscposcol = $ii;

	    }elsif ($hdrline[$ii] eq "4HPOSARO") {
	        $in4hposarocol = $ii;

	    }elsif ($hdrline[$ii] eq "4LPOSARO") {
	        $in4lposarocol = $ii;

	    }elsif ($hdrline[$ii] eq "4HPOSBRO") {
	        $in4hposbrocol = $ii;

	    }elsif ($hdrline[$ii] eq "4LPOSBRO") {
	        $in4lposbrocol = $ii;

	    }elsif ($hdrline[$ii] eq "AOPCADMD") {
	        $inaopcadmdcol = $ii;

	    }elsif ($hdrline[$ii] eq "CORADMEN") {
	        $incoradmencol = $ii;
	    }
    } # for ($ii=0; $ii<=$#hdrline; $ii++)

    my @inarr;
    my @outarr;
    my $outline;
    my $inline;
    my $preline;    
#
#--- remove whitespace line
#
    $preline = <ccdmfile>;

    $lasttime   = 0;
      
    while ($inline = <ccdmfile>) {
	    chomp $inline;
	    @inarr = split ("\t", $inline);
	
	    $outarr[$outtimecol] = &convert_time($inarr[$intimecol]);
	    if (int(($lasttime) / $resolution) == 
	        int (($outarr[$outtimecol]) / $resolution)) {
	        next;

	    } else {
	        $lasttime = $outarr[$outtimecol];
	        $outarr[$outtimecol] = sprintf("%e",
	        $outarr[$outtimecol] - ($outarr[$outtimecol] % $resolution));
	    }

	    $outarr[$outccsdstmfcol] = $inarr[$inccsdstmfcol];
	    $outarr[$outcobsrqidcol] = $inarr[$incobsrqidcol];
	    $outarr[$outcogeomtrcol] = $inarr[$incogeomtrcol];
    
	    if ($inarr[$in3tscposcol] >= 92703.0 && $inarr[$in3tscposcol] <= 94103.0) {
	        $outarr[$outsciinscol] = "ACIS-I";

	    } elsif ($inarr[$in3tscposcol] >= 74420 && $inarr[$in3tscposcol] <= 76820) {
	        $outarr[$outsciinscol] = "ACIS-S";

	    } elsif ($inarr[$in3tscposcol] >= -100800 && $inarr[$in3tscposcol] <= -98400) {
	        $outarr[$outsciinscol] = "HRC-S";

	    } elsif ($inarr[$in3tscposcol] >= -51705 && $inarr[$in3tscposcol] <= -49305) {
	        $outarr[$outsciinscol] = "HRC-I";

	    } else {
	        $outarr[$outsciinscol] = "INDEF";
	    }

	    $outarr[$out3faposcol]   = $inarr[$in3faposcol];
	    $outarr[$out4hposarocol] = $inarr[$in4hposarocol];
	    $outarr[$out4lposarocol] = $inarr[$in4lposarocol];

	    if ($inarr[$in4hposbrocol] <= 20.0) {
	        $outarr[$outgratingcol] = "HETG";

	    } elsif ($inarr[$in4lposbro] <= 20.0) {
	        $outarr[$outgratingcol] = "LETG";

	    } else {
	        $outarr[$outgratingcol] = "NONE";
	    }

	    $outarr[$outaopcadmdcol] = $inarr[$inaopcadmdcol];
	    $outarr[$outcoradmencol] = $inarr[$incoradmencol];
    
	    $outline = join ("\t", @outarr);
    
	    print OUTFILE $outline;
	    print OUTFILE "\n";
    }

    close ccdmfile;
}
	
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

sub parse_args {

    my $infile_found     = 0;
    my $outfile_found    = 0;
    my $resolution_found = 0;
    
    for ($ii = 0; $ii <= $#ARGV; $ii++) {
	    if (!($ARGV[$ii] =~ /^-/)) {
	        next;
	    }
#
#---  -i <infile>
#
	    if ($ARGV[$ii] =~ /^-i/) {
	        $infile_found = 1;

	        if ($ARGV[$ii] =~ /^-i$/) {
		        $ii++;
		        $infile = $ARGV[$ii];	    

	        } else {
		        $infile = substr($ARGV[$ii], 2);
	        }	    
	    } # if ($ARGV[$ii] =~ /^-p/)

#
#--- -o <outfile>
#
	    if ($ARGV[$ii] =~ /^-o/) {
	        $outfile_found = 1;

	        if ($ARGV[$ii] =~ /^-o$/) {
		        $ii++;
		        $outfile = $ARGV[$ii];	    

	        } else {
		        $outfile = substr($ARGV[$ii], 2);
	        }
	    } # if ($ARGV[$ii] =~ /^-o/)

#
#---  -r <resolution>
#
	    if ($ARGV[$ii] =~ /^-r/) {
	        $resolution_found = 1;

	        if ($ARGV[$ii] =~ /^-r$/) {
		        $ii++;
		        $resolution = $ARGV[$ii];	    

	        } else {
		        $resolution = substr($ARGV[$ii], 2);
	        }
	    } # if ($ARGV[$ii] =~ /^-o/)

#
#---  -v<verbose>
#
        if ($ARGV[$ii] =~ /^-v/) {
            $verbose_found = 1;
            if ($ARGV[$ii] =~ /^-v$/) {
                $ii++;
                $verbose = $ARGV[$ii];

            } else {
                $verbose = substr($ARGV[$ii], 2);
            }

        } # if ($ARGV[$ii] =~ /^-v/)
#
#---   -h
#
        if ($ARGV[$ii] =~ /^-h/) {
            goto USAGE;
        } # if ($ARGV[$ii] =~ /^-h/)

    } #  for ($ii = 0; $ii <= $#ARGV; $ii++)

    if (!$infile_found || !$outfile_found) {
        goto USAGE;
    }

    return;

    USAGE:
    print "Usage:\n\t$0 -i<infile> -o<outfile> -r<resolution> [-v<verbose>]\n";
    exit (0);
}

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#-------------------------------------------------------------------

sub convert_time {

    my @yrday    = split(' ', $_[0]);
    my $year     = $yrday[0];
    my $day      = $yrday[1];
    
    my @hrminsec = split(':', ($yrday[2] . $yrday[3]));
    my $hour     = $hrminsec[0];
    my $min      = $hrminsec[1];
    my $sec      = $hrminsec[2];

    my $totsecs  = 0;
    $totsecs     = $sec;
    $totsecs    += $min  * 60;
    $totsecs    += $hour * 3600;

    my $totdays  = 0;
    my $totdays  = $day-1;

    if ($year >= 98) {
	    $year = 1998 + ($year - 98);

    } else { 
        $year = 2000 + $year;
    }
#
#---  add days for past leap years
#
    if ($year > 2000) {
#
#--- add one for y2k
#
	    $totdays++;
#
#--- Number of years since 2000. -1 for already counted current leap
#
	    $years = $year - 2000 - 1;
	    $leaps = int ($years / 4);
	    $totdays += $leaps;
    }
    
    $totdays += ($year - 1998) * 365;
    $totsecs += $totdays * 86400;

    return $totsecs;
}
