#!/usr/bin/env /usr/local/bin/perl
use PGPLOT;

#########################################################################################################
#                                                                                                       #
#               cleano.pl: clean-up OTG move summary file                                               #
#                                                                                                       #
#               author:  Robert Cameron (June 2001)                                                     #
#                        B. Spitzbart (bspitzbart@cfa.harvard.edu)                                      #
#               modified by: t. isobe (tisobe@cfa.harvard.edu)                                          #
#                                                                                                       #
#               Last update:    Nov 19, 2015                                                            #
#                                                                                                       #
#########################################################################################################

#
#---- set output directory and rdb file names
#
$arc_dir = "/data/mta/www/mta_otg";
#$arc_dir = "./";


$f       = $arc_dir."/OTG_summary.rdb";
$f1      = $arc_dir."/OTG_filtered.rdb";
$f2      = $arc_dir."/OTG_sorted.rdb";
#
#--- read the summary file
#
open (R, $f) or die "Cannot open RDB file $f\n";

@f = <R>;
$hdr1 = shift @f;
$hdr2 = shift @f;
@a    = r2ah($hdr1,@f);
#
#--- make an index array of unique records
#
foreach $i (0..$#a) {
    push @g,  $a[$i]{GRATING};
    push @d,  $a[$i]{DIRN};
    push @t0, $a[$i]{START_TIME};
    push @t1, $a[$i]{STOP_TIME};
}

foreach $i (0..$#a-1) {
    $ok  = 1;
    $gi  = $g[$i];
    $di  = $d[$i];
    $t0i = $t0[$i];
    $t1i = $t1[$i];

    foreach $j ($i+1..$#a) {
	    next unless ($g[$j] eq $gi and $d[$j] eq $di);
	    $t0j = $t0[$j];
	    $t1j = $t1[$j];
	    $dt  = abs($t0i - $t0j) + abs($t1i - $t1j);
	    $t0  = ($t0i > $t0j)? $t0i : $t0j;
	    $t1  = ($t1i < $t1j)? $t1i : $t1j;
	    next unless ($dt < ($t1 - $t0)/10);
	    $ok = 0;
	    last;
    }
    push @i,$i if ($ok);
}
push @i,$#a;
#
#--- remove duplicates
#
@au = @a[@i];
#
#--- sort filtered array only by START_TIME
#
@as1 = sort { $a->{START_TIME} <=> $b->{START_TIME} } @au;
#
#--- sort filtered array by GRATING, then DIRN, then START_TIME
#
@as2 = sort { $a->{GRATING} cmp $b->{GRATING} || $a->{DIRN} cmp $b->{DIRN}
              || $a->{START_TIME} <=> $b->{START_TIME} } @au;
#
#--- apply the sorting to the original data
#
foreach $i (0..$#as1) { push @is1,$as1[$i]{ORD} };
foreach $i (0..$#as2) { push @is2,$as2[$i]{ORD} };
@fs1 = @f[@is1];
@fs2 = @f[@is2];
#
#--- make trend plots using START_TIME sorted hash
#
#############&plot_trends(@as1);    #---- temporarily removed Jan 10, 2019
#
#--- make html summary file
#
&sum_file;
#
#--- write filtered and sorted RDB files, text and html (BS June 2001) versions
#
open (R, ">$f1") or die "Cannot open RDB file $f1\n";
print R $hdr1;
print R $hdr2;
foreach (@fs1) { print R $_ };
#
#--- show all filtered (time sorted) moves
#
unshift(@fs1, $hdr1);

&mk_html($f1, @fs1);
#
#--- show only last 25 entries - watch it, this is destructive to @fs1
#
splice(@fs1, 0, $#fs1 - 24);
unshift(@fs1, $hdr1);

&mk_html(substr($f1,0,index($f1,".rdb"))."_short.rdb", @fs1);

open (R, ">$f2") or die "Cannot open RDB file $f2\n";
print R $hdr1;
print R $hdr2;
foreach (@fs2) { print R $_ };
#
#--- show all sorted (DIRN, GRATING, TIME)  moves
#
unshift(@fs2, $hdr1);

&mk_html($f2, @fs2);

#------------------------------------------------------------------------------------
#-- r2ah: convert an RDB array into an array of hash references                    --
#--       and add an ordinate to each hash, used for later sorting                 --
#------------------------------------------------------------------------------------

sub r2ah{

    my ($hdr,@rex) = @_;
    my @a   = ();
    my $ord = 0;
    chomp $hdr;
    @hdr    = split /\t/, $hdr;

    foreach (@rex) {
	    chomp;
	    @r = split /\t/;
	    $h = {};

	    foreach $i (0..$#r) { $h->{$hdr[$i]} = $r[$i] };

	    $h->{ORD} = $ord;
	    $ord++;
	    push @a, $h;
    }
    return (@a);
}

#------------------------------------------------------------------------------------
#-- plot_trends: plot time vs value for relevent columns                          ---
#------------------------------------------------------------------------------------

sub plot_trends {

    my @data = @_;
    
    my @trend_cols = qw(N_MOVES N_LONG T_LONG N_SHORT i4HPOSARO i4HPOSBRO f4HPOSARO f4HPOSBRO  \
                        EMF_MIN_LONG EMF_AVG_LONG EMF_MAX_LONG EMF_MIN_SHORT EMF_AVG_SHORT     \
                        EMF_MAX_SHORT OBC_ERRS);
#
#--- assume I'm given the data already sorted by START_TIME
#
    my $min_time = date2dom($data[0]->{START_TIME});
    my $max_time = date2dom($data[$#data]->{STOP_TIME});
#
#--- separate moves by grating and direction
#
    my %moves;
    my $grat; my $dirn; my $label;

    for ($i=0; $i<=$#data; $i++) {
        $grat  = $data[$i]->{GRATING};
        $dirn  = $data[$i]->{DIRN};
        $label = $grat."_".$dirn;
        push (@{$moves{$label}}, $i);
    }
#
#--- make plots.  
#
    my @xvals; my @yvals;
    foreach $name (@trend_cols) {

        $pltname = "$arc_dir/"."$name".".gif";

        pgbegin(0, "pgplot.ps/cps", 1,4);
        pgsubp(1,4);
        pgpap(0,1.4);
        pgslw(2.0);
        pgsch(2.2);

        foreach $label (qw(HETG_INSR HETG_RETR LETG_INSR LETG_RETR)) {
#
#--- should get label from keys(%moves), but don't know what 
#---  order they will be in, so the order is defined with the array above
#
            for ($i=0; $i<=$#{$moves{$label}}; $i++) {
                push @xvals, date2dom(@data[${moves{$label}}[$i]]->{START_TIME});
                push @yvals, @data[${moves{$label}}[$i]]->{$name};
            }
#
#--- find y-axis range, and set some scales
#
            my @ytmp = sort { $a <=> $b } @yvals;
            my $min_valu = $ytmp[0];
            my $max_valu = $ytmp[$#ytmp];
            if ($min_valu == $max_valu) { $max_valu += 0.1; }
            my $xbuff = ($max_time - $min_time) / 10;
            my $ybuff = ($max_valu - $min_valu) / 10;

            pgsci(1);
            pgenv($min_time-$xbuff,$max_time+$xbuff,$min_valu-$ybuff,$max_valu+$ybuff,0,0);
            pglab ("Time (DOM)", $name, $label);
            pgsci(8);
            pgpt ($#xvals+1, \@xvals, \@yvals, 2);
            @xvals=(); @yvals=();
        }
        pgclos();
        system("echo ''|gs -sDEVICE=ppmraw -r400 -g3500x2500 -q -NOPAUSE -sOutputFile=-  ./pgplot.ps|pnmflip -r270 |ppmtogif > $pltname");
        system("rm pgplot.ps");
    }
}

#------------------------------------------------------------------------------------
#-- mk_html: make html versions of original rdb summaries.                         --
#------------------------------------------------------------------------------------

sub mk_html {
    my ($name, @data) = @_;

    $name        = substr($name, 0,  index($name, ".rdb")).".html";
    my $path     = substr($name, 0, rindex($name, "/"));
    my $sum_file = "./gratstat.html";

    open (R, ">$name") or die "Cannot open html file $name\n";

    print R "<!DOCTYPE html>\n";
    print R "<html>\n";
    print R "<head>\n";
    print R "<title>OTG Move Summary<\/title>\n";
    print R "<\/head>\n";
    print R "<body text=\"#DDDDDD\" bgcolor=\"#000000\" link=\"#FF0000\" ";
    print R " vlink=\"#FFFF22\" alink=\"#7500FF\">\n";
    print R "<table border=1><tr>\n";
    print R "<td>PROC<\/td>\n";                           #--- links to processing summary

    my @hdr = split(/\t/,shift(@data));
#
#--- print column names and links to trend plots
#
    foreach (@hdr) {  
        s/\s+//g;
        if (-s $path."/".$_.".gif") {
            print R "<td><a href=\"$_.gif\">$_<\/a><\/td>\n";
        } else {
            print R "<td>$_<\/td>\n";
        }
    }
    print R "<\/tr>\n";

    foreach (reverse(@data)) { 
        my @line = split(/\t/, $_);
        my $graph = $line[1]."_".$line[0]."_".$line[2].".gif";
        s/\t/<\/td><td>/g;
        s/$/<\/td><\/tr>/;
        if (-s $path."/".$graph) {
            s/RETR<td>HETG<\/td><td>(.*?)<\/td><td>/RETR<\/td><td>HETG<\/td><td><a href=\"HETG_RETR_$1\.gif\">$1<\/a><\/td><td>/;
            s/INSR<td>HETG<\/td><td>(.*?)<\/td><td>/INSR<\/td><td>HETG<\/td><td><a href=\"HETG_INSR_$1\.gif\">$1<\/a><\/td><td>/;
            s/RETR<td>LETG<\/td><td>(.*?)<\/td><td>/RETR<\/td><td>LETG<\/td><td><a href=\"LETG_RETR_$1\.gif\">$1<\/a><\/td><td>/;
            s/INSR<td>LETG<\/td><td>(.*?)<\/td><td>/INSR<\/td><td>LETG<\/td><td><a href=\"LETG_INSR_$1\.gif\">$1<\/a><\/td><td>/;
        }
        my $proc = `grep $line[2] $path/$sum_file`;
        if ($proc ne "") {
            print R "<tr><td><a href=\"$sum_file\#$line[2]\">Summary<\/a><\/td><td>";
        } else {
            print R "<tr><td>\&\#160<\/td><td>";
        }
        print R $_ ;
    }
#    print R "<\/tr>\n";
    print R "<\/table>\n";
    print R "<\/body><\/html>\n";
    close R;
}

#------------------------------------------------------------------------------------
#-- date2dom: change date from format yyyydoy.hhmmsss to dom                      ---
#------------------------------------------------------------------------------------

sub date2dom {
    my $year = substr($_[0],  0, 4);
    my $doy  = substr($_[0],  4, 3);
    my $hour = substr($_[0],  8, 2);
    my $min  = substr($_[0], 10, 2);
    my $sec  = substr($_[0], 12, 2);
    
    my $days = ($year - 1999) * 365.0 + $doy - 203;
#
#--- add days for leap years
#
    my $leap = 2000;
    while ($year gt $leap) {
        ++$days;
        $leap += 4;
    }
    if ($year == $leap && $doy gt 59) { ++$days;}

    return ($days + $hour/24.0 + $min/1440.0 + $sec/86400.0);
}

#------------------------------------------------------------------------------------
#-- sum_file: add html tags to sum file, which are linked from html pages          --
#------------------------------------------------------------------------------------

sub sum_file {

    my $infile  = "/data/mta/Script/Dumps/gratstat.lis";
    my $outfile = "$arc_dir/gratstat.html";

    open(IN,  $infile);
    open(OUT, ">$outfile");

    print OUT "<!DOCTYPE html>\n";
    print OUT "<html>\n";
    print OUT "<head><title>grat stat</title></head>\n";
    print OUT "<body>\n";

    while ($line = <IN>) {
        if ($line =~ /PGPLOT/){
            next;
        }
        if ($line =~ /^\*/) {
            $save = $line;
            $chk  = 0;
        }
        if ($line =~ /No OTG moves found/) { next; }

        if($chk == 0){
            $save = $save.$line."<br />";

            if($line =~ /Move started at/){
                $label = substr($line, index($line, "at") + 3, 16);
                print OUT "<a name=$label>\n";
                print OUT $save.$line."<br />";
                $chk = 1;
            }
        } else {
            print OUT "$line<br />";
        }
    }
    print OUT "</body>\n";
    print OUT "</html>\n";
    close IN;
    close OUT;
}
