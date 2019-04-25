#!/usr/bin/perl

#---------------------------------------------------------------------------------
#
# pcadfilter.pl  This program is used to filter the input PRIMARYPCAD file
#                and convert the values to DataSeeker usable values
#                This final output is either appended to a new file or
#                a new table is created depending on whether or not
#                <outfile> exists
#                It also only samples the input file at <resolution> sec 
#                intervals
#   author: b. spitzbart (bspitzbart@cfa.harvard.edu)
#
#   modified by: t. isobe (tisobe@cfa.harvard.edu)
#   last update: Nov 09, 2015
#
#--------------------------------------------------------------------------------

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

my @pcadfiles;
my $pcadfile;
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
    while($pcadfile = <infile>) {
	    chomp $pcadfile;
	    $pcadfiles[$counter++] = $path . $pcadfile;
    }
}
else {
    $pcadfiles[0] = $infile;
}

my $hdr;
my @hdrline;
my $intimecol = 0;
#
#--- PCAD columns
#
my $inaoattqt1col = 0;    # S/C attitude: quat 1
my $inaoattqt2col = 0;    # S/C attitude: quat 2
my $inaoattqt3col = 0;    # S/C attitude: quat 3
my $inaoattqt4col = 0;    # S/C attitude: quat 4

#
#--- Get column information on the output PRIMARYPCAD file
#

my $outtimecol = 0;
#
#--- PCAD columns
#
my $outaoattrascol = 0;    # S/C attitude: ra
my $outaoattdeccol = 0;    # S/C attitude: dec
my $outaoattrolcol = 0;    # S/C attitude: roll

if (-e $outfile) {
    open OUTFILE, "<$outfile";

    $hdr = <OUTFILE>;
    
    chomp $hdr;
    @hdrline = split("\t", $hdr);
    for ($ii=0; $ii<=$#hdrline; $ii++) {

	    if ($hdrline[$ii] eq "time" || $hdrline[$ii] eq "TIME") {
	        $outtimecol = $ii;

	    } elsif($hdrline[$ii] eq "AOATTRAS") {
	        $outaoattrascol = $ii;

	    } elsif($hdrline[$ii] eq "AOATTDEC") {
	        $outaoattdeccol = $ii;

	    } elsif($hdrline[$ii] eq "AOATTROL") {
	        $outaoattrolcol = $ii;
	    }
    } # for ($ii=0; $ii<=$#hdrline; $ii++)
    
    close OUTFILE;

    open OUTFILE, ">>$outfile";

} else {

    $outtimecol     = 0;
    $outaoattrascol = 1;
    $outaoattdeccol = 2;    
    $outaoattrolcol = 3;    

    @hdrline = (
		"time", 
		"AOATTRAS", 
		"AOATTDEC", 
		"AOATTROL", 
		);

    open OUTFILE, ">$outfile";

    $hdr = join ("\t", @hdrline);

    print OUTFILE $hdr;
    print OUTFILE "\n";
    my @rdbTypeArr = ('N', 
		      'N',
		      'N',
		      'N');
    my $rdbTypeLine = join("\t", @rdbTypeArr);
    print OUTFILE $rdbTypeLine;
    print OUTFILE "\n";
}

foreach $file (@pcadfiles) {
    open pcadfile, "$file" or die;
    
    $hdr = <pcadfile>;
    chomp $hdr;
#
#--- Get column information on the input PRIMARYPCAD file
#
    
    @hdrline = split ("\t", $hdr);
    $intimecol = 0;
#
#--- PCAD columns
#
    $inaoattqt1col = 0;    # S/C attitude: quat 1
    $inaoattqt2col = 0;    # S/C attitude: quat 2
    $inaoattqt3col = 0;    # S/C attitude: quat 3
    $inaoattqt4col = 0;    # S/C attitude: quat 4
    
    for ($ii=0; $ii<=$#hdrline; $ii++) {

	    if ($hdrline[$ii] eq "TIME" || $hdrline[$ii] eq "time") {
	        $intimecol = $ii;
    
	    }elsif($hdrline[$ii] eq "AOATTQT1") {
	        $inaoattqt1col = $ii;
    
	    }elsif($hdrline[$ii] eq "AOATTQT2") {
	        $inaoattqt2col = $ii;
    
	    }elsif($hdrline[$ii] eq "AOATTQT3") {
	        $inaoattqt3col = $ii;
    
	    }elsif($hdrline[$ii] eq "AOATTQT4") {
	        $inaoattqt4col = $ii;
	    }
    }

    my @inarr;
    my @outarr;
    my $outline;
    my $inline;
    my $preline;
    
    my %radecrol;
#    
#--- remove whitespace line
#
    $preline = <pcadfile>;
    $lasttime = 0;
    
    while ($inline = <pcadfile>) {
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
    	
	    %radecroll = &quat_to_euler($inarr[$inaoattqt1col],
	                                $inarr[$inaoattqt2col],
	                                $inarr[$inaoattqt3col],
	                                $inarr[$inaoattqt4col]);
    	
    	
	    $outarr[$outaoattrascol] = sprintf("%e", $radecroll{ra});
	    $outarr[$outaoattdeccol] = sprintf("%e", $radecroll{dec});
	    $outarr[$outaoattrolcol] = sprintf("%e", $radecroll{roll});
    	
    	
	    $outline = join ("\t", @outarr);
    	
	    print OUTFILE $outline;
	    print OUTFILE "\n";
    } # while ($preline = <pcadfile>)

    close pcadfile;
}

close OUTFILE;

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

sub parse_args {

    my $infile_found     = 0;
    my $outfile_found    = 0;
    my $resolution_found = 0;

    
    for ($ii = 0; $ii <= $#ARGV; $ii++) {

	    if (!($ARGV[$ii] =~ /^-/)) {
	        next;
	    }
#
#---   -i <infile>
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
#---   -o <outfile>
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
#---   -v<verbose>
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
#---  -r<resolution>
#
        if ($ARGV[$ii] =~ /^-r/) {
            $resolution_found = 1;
    
            if ($ARGV[$ii] =~ /^-r$/) {
                $ii++;
                $resolution = $ARGV[$ii];
            } else {
                $resolution = substr($ARGV[$ii], 2);
            }
    
        } # if ($ARGV[$ii] =~ /^-v/)	
#
#---  -h
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
    print "Usage:\n\t$0 -i<infile> -o<outfile> [-r<resolution>] " .
	"[-v<verbose>]\n";
    exit (0);
}

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

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

    if ($year <= 1900) {
	    $year = 1998 + ($year - 98);
    }
#
#--- add days for past leap years
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

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

sub quat_to_euler {

    use Math::Trig;
    my @quat = @_;

    $RAD_PER_DEGREE = pi / 180.0;
    
    my $q1  = $quat[0];
    my $q2  = $quat[1];
    my $q3  = $quat[2];
    my $q4  = $quat[3];
    
    my $q12 = 2.0 * $q1 * $q1;
    my $q22 = 2.0 * $q2 * $q2;
    my $q32 = 2.0 * $q3 * $q3;
    
    my @T = (
	     [ 1.0 - $q22 - $q32, 2.0 * ($q1 * $q2 + $q3 * $q4), 2.0 * ($q3 * $q1 - $q2 * $q4) ],
	     [ 2.0 * ($q1 * $q2 - $q3 * $q4), 1.0 - $q32 - $q12,  2 * ($q2 * $q3 + $q4 * $q1) ],
	     [ 2.0 * ($q3 * $q1 + $q2 * $q4), 2.0 * ($q2 * $q3 - $q1 * $q4), 1.0 - $q12 - $q22 ]
	     );


    my %eci;

    $eci{ra}   = atan2($T[0][1], $T[0][0]);
    $eci{dec}  = atan2($T[0][2], sqrt($T[0][0] * $T[0][0] + $T[0][1] * $T[0][1]));
    $eci{roll} = atan2($T[2][0] * sin($eci{ra}) - $T[2][1] * cos($eci{ra}), -$T[1][0] * sin($eci{ra}) + $T[1][1] * cos($eci{ra}));
    

    $eci{ra}   /= $RAD_PER_DEGREE;
    $eci{dec}  /= $RAD_PER_DEGREE;
    $eci{roll} /= $RAD_PER_DEGREE;

    if ($eci{ra}   < 0.0)  {
	    $eci{ra} += 360.0;
    }
    if ($eci{roll} < -1e-13) {
        print hello;
	    $eci{roll} += 360.0;
    }
    if ($eci{dec}  < -90.0 || $eci{dec} > 90.0) {
	    print "Ugh dec $eci{dec}\n";
    }

    return (%eci);
}
