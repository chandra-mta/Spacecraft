#!/usr/bin/perl -w

my($buffer) = "";
open(FILE, "/etc/services") or
     die("Error reading file, stopped");
     while(read(FILE, $buffer, 100) == 10) {
        print("$buffer\n");
}
close(FILE);

