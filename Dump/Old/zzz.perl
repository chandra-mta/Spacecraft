#!/usr/bin/perl 

$ls{H} = [qw(4HILSA 4HRLSA 4HILSB 4HRLSB)];
$ls{L} = [qw(4LILSA 4LRLSA 4LILSBD 4LRLSBD)];

print "@ls\n";

foreach(@ls){
    print "I AM HERE\n";
    print "$_ <--->$ls{$_}i\n";
};
