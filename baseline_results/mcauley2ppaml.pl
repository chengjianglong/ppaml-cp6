#
# convert a set of mcauley labels_%02d-$label.txt files to a scorable file
# assumes that for any labels_NN_foo.txt, there is a labels_NN_foo.train.txt
# so that we can identify the image IDs to weed out from training
#

use strict;
die("Usage: $0 label-src-dir") unless (scalar(@ARGV)==1);
my $src_dir = shift(@ARGV);
my @label_fns = grep(/labels_\d\d_[A-z]+.txt$/, grep {!/\.train\.txt$/} glob($src_dir."/labels*.txt"));
print STDERR "Info: found ",scalar(@label_fns)," label files\n";

my $N_LABELS = 24;

my %t = ();  # key: image ID, val: ref to arry of (test) labels
for my $f (@label_fns) {
  my ($img, $conf, $label_id) = (undef, undef, undef);
  (my $train_f = $f) =~ s/\.txt$/.train.txt/;
  die("No training file $train_f") unless -f $train_f;
  if ($f =~ /labels_(\d+)_/) {
    $label_id = $1;
  } else {
    die("Couldn't parse label ID from $f");
  }

  # read the training image ids
  my %training_ids = ();
  open(F, $train_f) || die("Couldn't read $train_f");
  while (<F>) {
    if (/^ybar: \d+ [\-\d\.]+ label (\d+) conf [-\d\.]+ [\d\-\.]+\s*$/) {
      $training_ids{$1} = 1;
    } else {
      die("Couldn't parse img / conf from $train_f line $.\n$_\n");
    }
  }
  close F;


  open(F, $f) || die("Couldn't read $f");
  while (<F>) {
    # ybar: 0 -1 label 2144 conf -1 -0.000187
    if (/^ybar: \d+ [\-\d\.]+ label (\d+) conf [-\d\.]+ ([\d\-\.]+)\s*$/) {
      ($img, $conf) = ($1, $2);
    } else {
      die("Couldn't parse img / conf from $f line $.\n$_\n");
    }
    next if defined( $training_ids{$img} );

    if (!defined( $t{$img} )) {
      my @v = (0) x $N_LABELS;
      $t{$img} = \@v;
    }
    my $r = $t{$img};
    $$r[$label_id] = $conf;
  }
  close F;
}

for my $img_id (sort {$a<=$b} keys %t ) {
  my $r = $t{$img_id};
  print $img_id," ",join(" ",@{$r}),"\n";
}
