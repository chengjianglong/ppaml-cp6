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
## Header lines:
##
## [1] index:         label index
## [2] label:         label string
##
## [3] MAP:           mean average precision
## [4] n-predictions: number of predictions (non-zero scores) used in computing MAP
## [5] BER:  balanced error rate
##
## [6] n-instances:   number of positive / negative examples of the label
## [7] n-correct:     number of positive / negative examples correctly labeled
## [8] %-correct:     computed as [7]/[6]
##
## [9]  n-true-pos:        number of true positive examples
## [10] n-est-pos-correct: number of estimated positive results that were correct
## [11] pD:                probability of detection; [10] / [9]
## [12] n-est-pos-wrong:   number of estimated positive results that were incorrect
##
## [13] n-true-neg:        number of true negative examples
## [14] n-est-neg-correct: number of estimated negative results that were correct
## [15] n-est-neg-wrong:   number of estimated negative results that were incorrect
##
## Notes:
##
## a) [10] + [12] + [14] + [15] == [6]
## b) [10] + [15] == [9]
## c) [12] + [14] == [13]
##
## colloquial interpretations:
## [10]: "We asserted the label is present, and were correct-- we got it!"
## [12]: "We asserted the label is present, but were wrong-- false positive"
## [14]: "We asserted the label is absent, and were correct-- true negative"
## [15]: "We asserted the label is absent, and were wrong-- we missed it."
##

import sys
from cp6.utilities.util import Util
from cp6.tables.image_table import ImageTable
from cp6.utilities.image_table_entry import ImageTableEntry
from cp6.tables.label_table import LabelTable

if len(sys.argv) != 5:
    sys.stderr.write('Usage: $0 label-table image-table-truth image-table-computed threshold-table-computed\n')
    sys.exit(1)

lt = LabelTable.read_from_file( sys.argv[1] )
sys.stderr.write('Info: read %d labels\n' % len(lt.idset))

true_it = ImageTable.read_from_file( sys.argv[2] )
sys.stderr.write('Info: read %d answer-key entries\n' % len( true_it.entries ))

nLabels = len(lt.idset)

##
## Allow partial image tables with only image IDs and label vectors
##

n_fields = 0
with open( sys.argv[3] ) as f:
    n_fields = len(f.readline().split())

if n_fields == nLabels + 1:
    # attempt to read as a scoring-only pseudo-image-table
    computed_it = ImageTable()
    with open( sys.argv[3] ) as f:
        while 1:
            raw_line = f.readline()
            if not raw_line:
                break
            fields = raw_line.split()
            if len(fields) != (nLabels+1):
                raise AssertionError('Attempted to read %s as a score-only pseudo-image-table, but found %d fields on line %d; expected %d\n' % \
                                    (len(fields), len(t.entries)+1, (nLabels+1)))
            e = ImageTableEntry()
            e.mir_id = int(fields[0])
            e.label_vector = map(float, fields[1:])
            computed_it.entries[ e.mir_id ] = e

else:
    # read as a full-up image table
    computed_it = ImageTable.read_from_file( sys.argv[3] )

sys.stderr.write('Info: read %d computed entries\n' % len(computed_it.entries ))

with open( sys.argv[4] ) as f:
    threshold_table = map( float, f.readline().split() )

if len( threshold_table ) != len( lt.idset ):
    sys.stderr.write('Error: found %d thresholds, expected %d; exiting\n' % (len(threshold_table), len(lt.idset)))
    sys.exit(1)

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
sys.stdout.write('"index","label","MAP","n-predictions","BER","n-instances","n-correct","%-correct","n-true-pos","n-est-pos-correct","pD","n-est-pos-wrong","n-true-neg","n-est-neg-correct","n-est-neg-wrong"\n')

for i in range(0, nLabels):
    # create mapping from computed score to correct/incorrect
    # ...need to allow for duplicate score values! Python doesn't seem
    # to have a native multimap :(

    t = threshold_table[i]
    score_map = dict()  # key: image_id, val: score
    correct_map = dict() # key: image_id, val: True if correct, False if not

    (n_instances, n_true_pos, n_computed_pos_correct, n_computed_pos_wrong, n_true_neg, n_computed_neg_correct, n_computed_neg_wrong) = (0,0,0,0,0,0,0)

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
                n_computed_pos_correct += 1
            else:
                n_computed_neg_wrong += 1
        elif r == 0:
            n_true_neg += 1
            result = (s < t)
            if result:
                n_computed_neg_correct += 1
            else:
                n_computed_pos_wrong += 1
        else:
            raise AssertionError( 'Image %d label %d: unexpected label vector value %f\n' % (image_id, i, r))

        correct_map[ image_id ] = result

    if n_instances == 0:
        sys.stderr.write('Skipping label %d: %s\n'% (i,lt.id2label[i]))
        continue

    (n_predictions, n_correct_so_far, sum_ap) = (0, 0, 0)
    for (image_id, score) in sorted( score_map.items(), key=lambda x:-x[1]):
        # stop computing once we run out of non-zero responses
        if score > 0:
            n_predictions += 1
            if correct_map[ image_id ]:
                n_correct_so_far += 1
            this_ap = 1.0 * n_correct_so_far / n_predictions
            sum_ap += this_ap

    meanavgprec = 1.0*sum_ap / n_predictions if n_predictions > 0 else -1

    n_correct_total = correct_map.values().count( True )

    sys.stdout.write('%d,%s,' % (i, lt.id2label[i]))
    sys.stdout.write('%0.5f,%d,' % (meanavgprec, n_predictions) )
    ber_pos = (1.0 * n_computed_pos_correct / n_true_pos) / n_true_neg
    ber_neg = (1.0 * n_computed_neg_correct / n_true_neg) / n_true_pos
    ber = (ber_pos + ber_neg) / 2.0
    sys.stdout.write('%0.5f,' % ber )
    sys.stdout.write('%d,%d,%0.5f,' % (n_instances, n_correct_total, 1.0*n_correct_total/n_instances))
    sys.stdout.write('%d,%d,%0.5f,%d,' % (n_true_pos, n_computed_pos_correct, 1.0*n_computed_pos_correct / n_true_pos,n_computed_pos_wrong ))
    sys.stdout.write('%d,%d,%d\n' % (n_true_neg, n_computed_neg_correct,n_computed_neg_wrong))
