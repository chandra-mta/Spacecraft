#!/usr/bin/perl 

$k = 0;
open(FH, './zout');
while(read(FH, $out, 8)){
    print "$out\n";
    @buf = unpack('V2', $out);
    print "I AM HERE BUF: @buf\n";

    $k++;
    if ($k > 3){
        exit 1;
    }
}
close(FH);
