#
# Compute stats on edge tables:
# - per edge histograms of: n-group n-words user-flags
# - histogram of edges per node
# - histograms of entity_id counts in groups, words
#

use strict;

die("Usage: cat edge-table.txt | $0 output-prefix") unless (scalar(@ARGV)==1);

my $output_prefix = shift(@ARGV);

my %edges_per_node_hist = ();
my %ngroups_hist = ();
my %nwords_hist = ();
my %same_user_hist = ();
my %same_loc_hist = ();
my %same_contact_hist = ();
my %group_id_hist = ();
my %word_id_hist = ();
my %word_type_hist = ();

while (<STDIN>) {
  s/^\s*//;
  s/\s*$//;
  my @d = split(/\s+/);
  die("Expected 10 fields; found ".scalar(@d)) unless (scalar(@d)==10);
  ++$edges_per_node_hist{$d[0]};
  ++$edges_per_node_hist{$d[1]};
  ++$ngroups_hist{$d[2]};
  ++$nwords_hist{$d[3]};
  # d[4] is group list; d[5] is word list; d[6] is type list
  ++$same_user_hist{$d[7]};
  ++$same_loc_hist{$d[8]};
  ++$same_contact_hist{$d[9]};

  if ($d[4] eq "none") {
    ++$group_id_hist{0};
  } else {
    my @groups = split(/,/,$d[4]);
    die("Found ".scalar(@groups)." groups; expecting $d[2]") unless ($d[2] == scalar(@groups));
    for my $g (@groups) {
      ++$group_id_hist{$g};
    }
  }

  if ($d[5] eq "none") {
      ++$word_id_hist{0};
  } else {
    my @words = split(/,/,$d[5]);
    die("Found ".scalar(@words)." words; expecting $d[3]") unless ($d[3] == scalar(@words));
    for my $w (@words) {
      ++$word_id_hist{$w};
    }
  }

  if ($d[6] eq "none") {
      ++$word_type_hist{0};
  } else {
    my @word_types = split(/,/,$d[6]);
    die("Found ".scalar(@word_types)." word_types; expecting $d[3]") unless ($d[3] == scalar(@word_types));
    for my $wt (@word_types) {
      ++$word_type_hist{$wt};
    }
  }
}

write_hist(\%edges_per_node_hist, "${output_prefix}edges_per_node_hist.txt", 1);
write_hist(\%ngroups_hist, "${output_prefix}ngroups_hist.txt", 1);
write_hist(\%nwords_hist, "${output_prefix}nwords_hist.txt", 1);
write_hist(\%same_user_hist, "${output_prefix}same_user_hist.txt", 0);
write_hist(\%same_loc_hist, "${output_prefix}same_loc_hist.txt", 0);
write_hist(\%same_contact_hist, "${output_prefix}same_contact_hist.txt", 0);
write_hist(\%group_id_hist, "${output_prefix}group_id_hist.txt", 1);
write_hist(\%word_id_hist, "${output_prefix}word_id_hist.txt", 1);
write_hist(\%word_type_hist, "${output_prefix}word_type_hist.txt", 1);

exit(0);

##
##
##

sub write_hist
{
  my ($ref, $fn, $keys_are_numeric) = @_;
  open(F, ">$fn") || die("Couldn't write '$fn'");
  my @k =
    $keys_are_numeric
    ? sort {$a<=>$b} keys %$ref
    : sort keys %$ref;

  for my $key (@k) {
    print F "$key $$ref{$key}\n";
  }
  close F;
}
