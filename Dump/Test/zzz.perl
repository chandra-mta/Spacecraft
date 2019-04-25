#!/user/bin/perl 


$out = &bit(32, 10);


sub bit {
  local($off, $len) = @_;
  local($bit, $n, $exp, $i) = $off & 31;
  print "$bit, $n, $exp, $i\n";
  $out = 0x7fffffff >> ($bit -1);
  print "out: $out\n";
  $n &= 0x7fffffff >> ($bit -1);
  print "n: $n\n";
  if ($bit + $len > 32) {
    $n = $buf[$off >> 5] >> $bit;
    $n &= 0x7fffffff >> ($bit - 1) if $bit;
    $exp = 32 - $bit;
    $off += $exp;
    $len -= $exp;
    $bit = 0;
  }
  $i = $buf[$off >> 5] >> $bit;
  $i &= 0x7fffffff >> (31 - $len) if $len < 32;
  $n += $i << $exp;
  print "I AM HERE: $n\n";
  return $n;
}

