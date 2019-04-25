#!/usr/bin/perl -w
##!/proj/axaf/bin/perl -w

# analyze OTG moves

# Robert Cameron
# May 2001

######use PGPLOT;

#$arc_dir = "/home/rac/scratch";
$arc_dir = "/data/mta/www/mta_otg";

$ls{H} = [qw(4HILSA 4HRLSA 4HILSB 4HRLSB)];
$ls{L} = [qw(4LILSA 4LRLSA 4LILSBD 4LRLSBD)];
$pot{H} = [qw(4HPOSARO 4HPOSBRO)];
$pot{L} = [qw(4LPOSARO 4LPOSBRO)];

$ovc = "OFLVCDCT";
$cvc = "CCSDSVCD";

# read the telemetry file

%h = rtlog($ARGV[0]);

print "*"x70,"\nProcessing $ARGV[0]\n";

# shift the arrays of MSIDs 4HENLBX, 4HEXRBX, 4LENLBX, 4LEXRBX 
# by 1 element later to align with the back-emf telemetry

foreach (qw(4HENLBX 4HEXRBX 4LENLBX 4LEXRBX)) {
    @dum = @{$h{$_}};
    pop @dum;
    unshift @dum, $dum[0];
    @{$h{$_}} = @dum;
}

# define variable back-emf thresholds for long moves and nudges

#%thresh = (N => 5.8, L => 5.8, H => 5.8);               # for ASVT data
%thresh = (N => 3.9, L => 4.5, H => 4.5);  $ovc = $cvc; # for real data

# initial identification of moves, using back-emf

$pst = "N";
foreach $i (0..$#{$h{TIME}}) {
    $hen = $h{"4HENLBX"}[$i];
    $len = $h{"4LENLBX"}[$i];
    $a28 = $h{"4MP28AV"}[$i];
    $b28 = $h{"4MP28BV"}[$i];
    $a5  = $h{"4MP5AV"}[$i];
    $b5  = $h{"4MP5BV"}[$i];
    $st = "N";
    if ($a28 > $thresh{$pst} && $b28 > $thresh{$pst} && $a5 > 4.5 && $b5 > 4.5) {
	$st = "H" if ($hen eq "ENAB");
	$st = "L" if ($len eq "ENAB");
    }
    push @st, $st;
    $pst = $st;
#    print "$hen\t$len\t$a28\t$b28\t$a5\t$b5\t$st\n";
}

# find separate moves

%m = &find_moves();

# analyze the moves

@rex = sort numerically keys %m;
push @rex,$#st+1;
foreach $i (0..$#rex-1) {
    $ibeg = $rex[$i];
    $iend = $rex[$i+1]-1;
    $otg = $m{$ibeg};
    print "="x60,"\n";
    print "\n$otg","ETG move, between records $ibeg and $iend\n";
    &analyze_move();
}

sub numerically { $a <=> $b };

###*******************************************************************
##sub plot_move
##
## plot OTG move data
##
###*******************************************************************
#{
#    $k0 -= 1;
#    $k1 += 10;
#    $vx0 = $h{$cvc}[$k0];
#    @tx  = map { ($_ - $vx0) * 0.25625 } @{$h{$cvc}}[$k0..$k1];
#    @a5  = @{$h{"4MP5AV"}}[$k0..$k1];
#    @b5  = @{$h{"4MP5BV"}}[$k0..$k1];
#    @a28 = @{$h{"4MP28AV"}}[$k0..$k1];
#    @b28 = map { $_ - 20 } @{$h{"4MP28BV"}}[$k0..$k1];
#    @ap  = @{$h{$pot{$otg}[0]}}[$k0..$k1];
#    @bp  = @{$h{$pot{$otg}[1]}}[$k0..$k1];
#    @exs  = @{$h{"4".$otg."EXRBX"}}[$k0..$k1];
#    @ens  = @{$h{"4".$otg."ENLBX"}}[$k0..$k1];
#    @exv = map { ($_ eq "ENAB")? 11.5 : 11 } @exs;
#    @env = map { ($_ eq "ENAB")? 10.5 : 10 } @ens;
#    $npt = $#tx + 1;
#
#    @linex = (0, $tx[-1]);
#    @liney = (10,10);
#
#    $pltname = $otg."ETG_".$dir."_$t0.gif";
#    pgbegin (0,"$arc_dir/$pltname/gif",1,2);
##    pgpap(8,0.7);
#    pgsch(1.5);
#
#    pgenv(0,$tx[-1],0,90,0,0);
#    pglab ("Time (seconds)", "Pot Angle (deg)", $pltname);
#    pgsci(8);
#    pgline ($npt, \@tx, \@ap);
#    pgtext ($tx[-1]*0.0, 93, $pot{$otg}[0]);
#    pgsci(5);
#    pgline ($npt, \@tx, \@bp);
#    pgtext ($tx[-1]*0.15, 93, $pot{$otg}[1]);
#
#    pgsci(1);
#    pgenv(0,$tx[-1],0,12,0,0);
#    pglab ("Time (seconds)", "Voltage (V)", "");
#    pgline (2, \@linex, \@liney);
#    pgsci(3);
#    pgline ($npt, \@tx, \@exv);
#    pgtext ($tx[-1]*0.9, 12.5, "4".$otg."EXRBX");
#    pgsci(2);
#    pgline ($npt, \@tx, \@env);
#    pgtext ($tx[-1]*0.8, 12.5, "4".$otg."ENLBX");
#    pgsci(8);
#    pgline ($npt, \@tx, \@a5);
#    pgtext ($tx[-1]*0.0, 12.5, "4MP5AV");
#    pgsci(5);
#    pgline ($npt, \@tx, \@b5);
#    pgtext ($tx[-1]*0.1, 12.5, "4MP5BV");
#    pgsci(10);
#    pgline ($npt, \@tx, \@a28);
#    pgtext ($tx[-1]*0.2, 12.5, "4MP28AV");
#    pgsci(7);
#    pgline ($npt, \@tx, \@b28);
#    pgtext ($tx[-1]*0.3, 12.5, "4MP28BV-20V");
#
##    pgiden;
#    pgend;
#}

##*******************************************************************
sub find_moves
#
# find separate OTG moves
#
##*******************************************************************
{
    unless (grep /(L|H)/, @st) { print "No OTG moves found.\n"; exit };

# find start, stop and type of all moves

    $pst = "N";
    foreach $i (0..$#st) {
	next if ($st[$i] eq $pst);
	if ($pst ne "N" && $st[$i] ne "N") { print "Bad state transition at record $i: $pst to $st[$i]. Stopping!\n"; exit };
	if ($pst eq "N") { $i0 = $i } else { push @m0,$i0; push @m1,$i; push @mg,$pst };
	$pst = $st[$i];
    }
    unless (@m0) { print "No OTG moves found. Stopping!\n"; exit };

# revise start and stop of long moves, based on bi-level telemetry

    foreach $i (0..$#m0) {
	$ml = $m1[$i] - $m0[$i] - 1;
	next if ($ml < 10);
	$otg = $mg[$i];
	$otg2 = $otg."ETG";
	$ben = "4".$otg."ENLBX";
	$bex = "4".$otg."EXRBX";
	$j0 = $m0[$i] - 2;
	$j0 = 0 if ($j0 < 0);
	$j1 = $m1[$i] + 2;
	$j1 = $#st if ($j1 > $#st);
	$nl = 0;
	print "\nRevising long $otg2 move between records $j0 and $j1.\n";
	foreach ($j0..$j1) {
	    $st[$_] = "N";
	    next unless ($h{$ben}[$_] eq "ENAB" && $h{$bex}[$_] eq "ENAB");
	    $st[$_] = $otg;
	    $nl++;
	}
	print "\n >>WARNING! Large revision in move length at record $m0[$i]: $ml to $nl\n" if (abs($ml - $nl) > 3);
    }

# report revised long moves

    $pst = "N";
    foreach $i (0..$#st) {
	next if ($st[$i] eq $pst);
	if ($pst ne "N" && $st[$i] ne "N") { print "Bad state transition at record $i: $pst to $st[$i]. Stopping!\n"; exit };
	if ($pst eq "N") { $i0 = $i } else { $m{$i0} = $pst if ($i - $i0) > 100 };
	$pst = $st[$i];
    }
    unless (%m) { print "No long OTG moves found. Stopping!\n"; exit };
    return %m;
}

##*******************************************************************
sub analyze_move
#
# report data on OTG move
#
##*******************************************************************
{
    my @i0 = ();
    my @i1 = ();
    my @dt = ();
    my @emf_l = ();
    my @emf_s = ();
    my @arc = ();
    @ls  = @{$ls{$otg}};
    @pot = @{$pot{$otg}};
    push @arc,$otg."ETG";

# find moves

    $pst = "N";
    foreach $i ($ibeg..$iend) {
	push @i0,$i if ($pst eq "N" && $st[$i] eq $otg);
	push @i1,$i if ($pst eq $otg && $st[$i] eq "N");
	$pst = $st[$i];
    }
    if ($#i0 != $#i1) { print "Oops! Found ",$#i0+1," move starts and ",$#i1+1," move stops.\n"; return };
    print "\n >>WARNING! Move starts at data record $i0[0]\n" if ($i0[0] < 5);
    print "\n >>WARNING! Move ends at data record $i1[-1]\n" if ($#st-$i1[-1] < 5);

# move times

    $t0 = $h{TIME}[$i0[0]];
    $t1 = $h{TIME}[$i1[-1]];
    print "\n Move started at $t0; VCDU = $h{$ovc}[$i0[0]]\n";
    print " Move stopped at $t1; VCDU = $h{$ovc}[$i1[-1]]\n";
    print "\n Number of movements = ",$#i0+1,"\n";
    $vcdu = sprintf "%10d",$h{$ovc}[$i0[0]];
    push @arc,$t0,$vcdu;
    $vcdu = sprintf "%10d",$h{$ovc}[$i1[-1]];
    push @arc,$t1,$vcdu;
    $nl = 0;
    $tl = 0;
    $ns = 0;
    print " Move durations (seconds):\n";
    foreach $i (0..$#i0) { 
	$dt = ($h{$cvc}[$i1[$i]] - $h{$cvc}[$i0[$i]]) * 0.25625;
	push @dt,$dt;
	if ($dt > 100) { for ($i0[$i]..$i1[$i]-1) { push @emf_l,$h{"4MP28AV"}[$_] }; $nl++; $tl += $dt };
	if ($dt < 2)   { for ($i0[$i]..$i1[$i]-1) { push @emf_s,$h{"4MP28AV"}[$_] }; $ns++ };
	printf "%6d: %8.3f\n",$i+1,$dt[$i];
    }
    $tl = sprintf "%.3f",$tl;
    push @arc,$#i0+1,$nl,$tl,$ns;

# limit switch data

    print "\n Limit Switch states:\n";
    $j = 0;
    while ($h{"4MP5AV"}[$i0[0]-$j] > 4.5 && $h{"4MP5BV"}[$i0[0]-$j] > 4.5 && $j < 5) { $j++ };
    $j--;
    $k = $i0[0]-2 if ($j > 2);
    $k = $i0[0]-1 if ($j == 2);
    $k = $i0[0]   if ($j < 2);
    print "  Pre-move:  (Time = $h{TIME}[$k])\n";
    foreach (@ls) { printf "   %-7s = %s\n",$_,$h{$_}[$k]; push @arc,$h{$_}[$k] };
    $j = 0;
    while ($h{"4MP5AV"}[$i1[-1]+$j] > 4.5 && $h{"4MP5BV"}[$i1[-1]+$j] > 4.5 && $j < 5) { $j++ };
    $j--;
    $k = $i1[-1]+2 if ($j > 2);
    $k = $i1[-1]+1 if ($j == 2);
    $k = $i1[-1]   if ($j < 2);
    print "  Post-move: (Time = $h{TIME}[$k])\n";
    foreach (@ls) { printf "   %-7s = %s\n",$_,$h{$_}[$k]; push @arc,$h{$_}[$k] };

# potentiometer data

    print "\n Potentiometer Angles (degrees):\n";
    $k0 = ($i0[0]-2 < 0)? 0 : $i0[0]-2;
    $err0 = $h{COERRCN}[$k0];
    print "  Pre-move:  (Time = $h{TIME}[$k0])\n";
    foreach (@pot) { print "   $_ = $h{$_}[$k0]\n"; push @arc,$h{$_}[$k0] };
    @pot0 = @arc[-2,-1];
    $k1 = ($i1[-1]+2 > $#st)? $#st : $i1[-1]+2;
    $err1 = $h{COERRCN}[$k1];
    print "  Post-move: (Time = $h{TIME}[$k1])\n";
    foreach (@pot) { print "   $_ = $h{$_}[$k1]\n"; push @arc,$h{$_}[$k1] };
    @pot1 = @arc[-2,-1];

# move direction

    $dir = "UNDF";
    $dir = "INSR" if ($pot0[0] > $pot1[0] && $pot0[1] > $pot1[1]);
    $dir = "RETR" if ($pot0[0] < $pot1[0] && $pot0[1] < $pot1[1]);
    print "\n Move Direction = $dir\n";
    unshift @arc,$dir;

# back-emf data

    print "\n Back-emf statistics:\n";
    if (@emf_l) { 
	print "  Long moves:\n";
	($emf_min,$emf_avg,$emf_max) = emf_stats(@emf_l);
	print "   Min. back-emf (V) = $emf_min\n"; 
	print "   Avg. back-emf (V) = $emf_avg\n"; 
	print "   Max. back-emf (V) = $emf_max\n"; 
	push @arc,$emf_min,$emf_avg,$emf_max;
    } else { push @arc,0.0,0.0,0.0 };
    if (@emf_s) { 
	print "  Short moves:\n";
	($emf_min,$emf_avg,$emf_max) = emf_stats(@emf_s);
	print "   Min. back-emf (V) = $emf_min\n"; 
	print "   Avg. back-emf (V) = $emf_avg\n"; 
	print "   Max. back-emf (V) = $emf_max\n"; 
	push @arc,$emf_min,$emf_avg,$emf_max;
    } else { push @arc,0.0,0.0,0.0 };

# OBC error count

    print "\n OBC Error Count increment = ",$err1-$err0,"\n";
    push @arc,$err1-$err0;

# print summary record to archive

    $sumfile = "$arc_dir/OTG_summary.rdb";
    open (SF, ">>$sumfile") or die "Cannot open OTG summary file $sumfile\n";

    &prep_file() if ( -z $sumfile);
    foreach (0..17) { print SF "$arc[$_]\t" };
    foreach (18..27) { printf SF "%.2f\t", $arc[$_] };
    print SF "$arc[-1]\n";

    print "\nMove data record appended to $sumfile\n";

# plot move data

###    &plot_move();        #--- temporaryly commented out
}

##*******************************************************************
sub prep_file
#
# write header lines to summary file
#
##*******************************************************************
{
    @pre_ls = map { "i".$_ } @ls;
    @post_ls = map { "f".$_ } @ls;
    @pre_pot = map { "i".$_ } @pot;
    @post_pot = map { "f".$_ } @pot;
    @hdr1 = qw(DIRN GRATING START_TIME START_VCDU STOP_TIME STOP_VCDU N_MOVES N_LONG T_LONG N_SHORT);
    @hdr2 = qw(EMF_MIN_LONG EMF_AVG_LONG EMF_MAX_LONG EMF_MIN_SHORT EMF_AVG_SHORT EMF_MAX_SHORT OBC_ERRS);
    @typ = qw(S S N N N N N N N N S S S S S S S S N N N N N N N N N N N);

    foreach (@hdr1,@pre_ls,@post_ls,@pre_pot,@post_pot) { print SF "$_\t" };
    foreach (0..$#hdr2-1) { print SF "$hdr2[$_]\t" };
    print SF "$hdr2[-1]\n";
    foreach (0..$#typ-1) { print SF "$typ[$_]\t" };
    print SF "$typ[-1]\n";

    print "\nRDB header records output to $sumfile";
}

##*******************************************************************
sub emf_stats
#
# calculate back-emf statistics
#
##*******************************************************************
{
    my (@emf) = @_;
    my $emf_avg = 0;
    my $emf_min = 999;
    my $emf_max = -999;
    foreach (@emf) { 
	$emf_avg += $_;
	$emf_min = $_ if ($_ < $emf_min);
	$emf_max = $_ if ($_ > $emf_max);
    }
    $emf_avg /= ($#emf + 1);
    $emf_avg = sprintf "%.2f", $emf_avg;
    return ($emf_min,$emf_avg,$emf_max);
}

##*******************************************************************
sub rrdb
#
# read an RDB file into a hash of arrays
#
##*******************************************************************
{
    my ($f) = @_;
    my %h = ();
    open (R, $f) or die "Cannot open RDB file $f\n";
    $fields = <R>;
    chomp $fields;
    @hdr = split /\t/, $fields;
    $fields = <R>;
    @rex = <R>;
#    print STDERR "%RRDB: $f:  ",$#rex+1," input records of ",$#hdr+1," fields.\n";
    foreach (@rex) {
	chomp;
	@r = split /\t/;
	foreach $i (0..$#r) { push @{$h{$hdr[$i]}},$r[$i] };
    }
    close R;
    return (%h);
}

##*******************************************************************
sub rtlog
#
# read an ACORN tracelog file into a hash of arrays
#
##*******************************************************************
{
    my ($f) = @_;
    my %h = ();
    open (R, $f) or die "Cannot open tracelog file $f\n";
    $fields = <R>;
    chomp $fields;
    @hdr = split /\t/, $fields;
    $fields = <R>;
    @rex = <R>;
#    print STDERR "%RTLOG: $f:  ",$#rex+1," input records of ",$#hdr+1," fields.\n";
    foreach (@rex) {
	chomp;
	@r = split /\t/;
	foreach $i (0..$#r) { 
          $_ = $r[$i];
          s/^\s+//;
          s/\s+$//;
          s/\:\s/\:0/g;
          s/\s/_/g;
          push @{$h{$hdr[$i]}},$_;
        }
    }
    close R;
    return (%h);
}
