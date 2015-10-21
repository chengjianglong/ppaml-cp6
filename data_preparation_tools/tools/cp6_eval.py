# Copyright 2015 Kitware, Inc.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

#  * Neither name of Kitware, Inc. nor the names of any contributors may be used
#    to endorse or promote products derived from this software without specific
#    prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Part of the DARPA PPAML CP6 toolset; poc: roddy.collins@kitware.com
#

##
## Generate CP6 metrics.
##
##
##

import sys
from cp6.utilities.util import Util
from cp6.tables.image_table import ImageTable
from cp6.tables.label_table import LabelTable

if len(sys.argv) != 5:
    sys.stderr.write('Usage: $0 label-table image-table-truth image-table-computed threshold-table-computed\n')
    sys.exit(1)

lt = LabelTable.read_from_file( sys.argv[1] )
sys.stderr.write('Info: read %d labels\n' % len(lt.idset))

true_it = ImageTable.read_from_file( sys.argv[2] )
sys.stderr.write('Info: read %d answer-key entries\n' % len( true_it.entries ))

computed_it = ImageTable.read_from_file( sys.argv[3] )
sys.stderr.write('Info: read %d computed entries\n' % len(computed_it.entries ))

with open( sys.argv[4] ) as f:
    threshold_table = map( float, f.readline().split() )

if len( threshold_table ) != len( lt.idset ):
    sys.stderr.write('Error: found %d thresholds, expected %d; exiting\n' % (len(threshold_table), len(lt.idset)))
    sys.exit(1)

nLabels = len(lt.idset)

#
# Compute mean average precision thusly:
#
# - for each label L:
#
# --- sort predictions for L by score
# --- for each prediction i in 0...#L:
# ------- compute nCorrect @ i / i (this is AP @i)
# ...then report average of all AP@i
#

# key: image id; val: 0x01 if in truth, 0x02 if in computed
image_id_state_map = { i:0x02 for i in computed_it.entries.keys() }
for i in true_it.entries.keys():
    v = 0x03 if i in image_id_state_map else 0x01
    image_id_state_map[i] = v

sys.stderr.write('Scored:     %d\n' % image_id_state_map.values().count( 0x03 ))
sys.stderr.write('Unscored:   %d\n' % image_id_state_map.values().count( 0x01 ))
sys.stderr.write('Extraneous: %d\n' % image_id_state_map.values().count( 0x02 ))

# emit CSV header
sys.stdout.write('"index","label","MAP","BER","n-instances","n-correct","%-correct","n-true-pos","n-computed-pos","n-true-neg","n-computed-neg"\n')

for i in range(0, nLabels):
    # create mapping from computed score to correct/incorrect
    # ...need to allow for duplicate score values! Python doesn't seem
    # to have a native multimap :(

    t = threshold_table[i]
    score_map = dict()  # key: image_id, val: score
    correct_map = dict() # key: image_id, val: True if correct, False if not

    (n_instances, n_true_pos, n_computed_pos, n_true_neg, n_computed_neg) = (0,0,0,0,0)

    for (image_id, true_image_entry) in true_it.entries.iteritems():
        if image_id_state_map[ image_id ] != 0x03:
            continue
        s = computed_it.entries[ image_id ].label_vector[ i ]
        r = true_image_entry.label_vector[ i ]
        if r == -1:
            # don't score this label; skip
            continue

        n_instances += 1
        score_map[ image_id ] = s
        if  r == 1:
            n_true_pos += 1
            result = (s >= t)
            if result:
                n_computed_pos += 1
        elif r == 0:
            n_true_neg += 1
            result = (s < t)
            if result:
                n_computed_neg += 1
        else:
            raise AssertionError( 'Image %d label %d: unexpected label vector value %f\n' % (image_id, i, r))

        correct_map[ image_id ] = result

    if n_instances == 0:
        sys.stderr.write('Skipping label %d: %s\n'% (i,lt.id2label[i]))
        continue

    (n_predictions, n_correct_so_far, sum_ap) = (0, 0, 0)
    for (image_id, score) in sorted( score_map.items(), key=lambda x:-x[1]):
        n_predictions += 1
        if correct_map[ image_id ]:
            n_correct_so_far += 1
        this_ap = n_correct_so_far / n_predictions
        sum_ap += this_ap

    n_correct_total = correct_map.values().count( True )
    if n_correct_total != n_correct_so_far:
        raise AssertionError('Logic error: label %d total correct %d vs n-so-far %d\n' % (i, n_correct_total, n_correct_so_far))

    sys.stdout.write('%d,%s,' % (i, lt.id2label[i]))
    sys.stdout.write('%0.5f,' % (sum_ap / n_instances))
    ber_pos = (n_computed_pos / n_true_pos) / n_true_neg
    ber_neg = (n_computed_neg / n_true_neg) / n_true_pos
    ber = (ber_pos + ber_neg) / 2.0
    sys.stdout.write('%0.5f,' % ber )
    sys.stdout.write('%d,%d,%0.5f,' % (n_instances, n_correct_total, 1.0*n_correct_total/n_instances))
    sys.stdout.write('%d,%d,%d,%d\n' % (n_true_pos, n_computed_pos, n_true_neg, n_computed_neg))
