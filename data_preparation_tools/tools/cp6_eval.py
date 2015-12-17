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
## [3] mAP:           mean average precision
## [4] n-predictions: number of predictions (non-zero scores) used in computing mAP
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
import argparse
import random

from cp6.utilities.util import Util
from cp6.tables.image_table import ImageTable
from cp6.utilities.image_table_entry import ImageTableEntry
from cp6.tables.label_table import LabelTable

##
## Terminology for mean average precision (mAP) as applied to PPAML CP6:
##
## N is the size of the entire set of test images; for any label, NRel
## is the number of test images which have that label.
##
## Query: One query per label: "What images have this label?" Returns a response
## set S of scores, |S| == N, such that S[i]>0 indicates some degree of confidence
## the label applies. S[i] <= 0 indicates no confidence the label applies.
## McAuley's code returns values [-1,1] with 0 being the binarization threshold,
## the sample CRF code returns values [0,1].
##
## Precision at k (P@k): Sort the response by score; take T == the top k responses.
## Let R == number of elements in T which are relevant (i.e. have the label.)
## Precision@k == R / k.
##
## Average precision (AP): Sort response set by score; sweep k from 1:N. At each
## k such that the k'th image has the label (i.e. relevant[k] == true), compute
## P@k. The AP is the average of P@k, i.e. the sum of P@k divided by the number
## of relevant retrievals (i.e. the number of images which truly have the label.)
##
## Mean average precision (mAP): The average of AP across the set of labels.
##

def mean(ls):
    return sum(ls) / len(ls)

def calculate_AP( relevant_map, score_map ):
    (n_retrievals, n_relevant_retrievals, sum_ap) = (0, 0, 0)
    for (image_id, score) in sorted( score_map.items(), key=lambda x:-x[1]):
        # stop "retrieving" once the score drops <=0
        if score <= 0:
            break
        n_retrievals += 1
        if relevant_map[ image_id ]:
            n_relevant_retrievals += 1
            sum_ap += 1.0 * n_relevant_retrievals / n_retrievals

    avgprec = 1.0*sum_ap / n_relevant_retrievals if n_relevant_retrievals > 0 else -1
    return (avgprec, n_retrievals)

# AP test case
def mk_correct_map():
    return { 0:1, 1:0, 2:1, 3:0, 4:1, 5:1}

def mk_score_map():
    return { 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

def float_test( msg, expected, actual, eps = 1.0e-4 ):
    sys.stderr.write( 'TEST: %s expected: %f actual: %f pass: %s\n' % (msg, expected, actual, (abs(expected-actual) < eps)))

def test_AP():
    (ap_1, n_1) = calculate_AP(mk_correct_map(), mk_score_map())
    float_test( 'AP test #1', 0.7333333333333333, ap_1 )

def test_mAP():
    #
    # based on slide 31 of https://www.cl.cam.ac.uk/teaching/2006/InfoRtrv/lec3.2.pdf
    #
    # set lower image IDs to have higher scores so they are "ranked" first
    #
    (q1_AP, n) = calculate_AP( {k: 1 if k in [1,3,6,10,20] else 0 for k in range(1, 21)}, \
                               {k:21-k for k in range(1,21)} )
    (q2_AP, n) = calculate_AP( {k: 1 if k in [1,3,15] else 0 for k in range(1, 16)}, \
                               {k:16-k for k in range(1,16)} )
    mAP = (q1_AP + q2_AP) / 2.0
    (expected_q1_AP, expected_q2_AP) = (0.564, 0.623)
    expected_mAP = (expected_q1_AP + expected_q2_AP) / 2.0
    float_test( 'AP test #2', expected_q1_AP, q1_AP, 0.001 )
    float_test( 'AP test #3', expected_q2_AP, q2_AP, 0.001 )
    float_test( 'mAP test #1', expected_mAP, mAP, 0.001 )

def main():

    # special-case the '--test' arg because the other options are 'required', and
    # we'd like to run with just '--test' without having to e.g. specify /dev/null
    # four times

    if sys.argv.count( '--test' ) > 0:
        test_AP()
        test_mAP()
        sys.exit(0)

    parser = argparse.ArgumentParser( description='PPAML CP6 evaluation' )
    parser.add_argument( '--r', '--rand', choices=['b','p'], help='b|p; Replace computed values with random 0/1 values over either [b]inary or [p]rior-of-truth distributions' )
    parser.add_argument( '--lt', required=True, help='Label table' )
    parser.add_argument( '--tt', required=True, help='Truth image table (aka answer key)' )
    parser.add_argument( '--ct', required=True, help='Computed image table (may be in reduced form)' )
    parser.add_argument( '--tht', required='True', help='Threshold table for converting soft thresholds into hard 0/1 values')

    # arg is added for help screen but acted on in special-case above
    parser.add_argument( '--test', action='store_true', help='Run some sanity tests and exit')

    args = parser.parse_args()

    lt = LabelTable.read_from_file( args.lt )
    sys.stderr.write('Info: read %d labels\n' % len(lt.idset))

    true_it = ImageTable.read_from_file( args.tt )
    sys.stderr.write('Info: read %d answer-key entries\n' % len( true_it.entries ))

    nLabels = len(lt.idset)

##
## Allow partial image tables with only image IDs and label vectors
##

    n_fields = 0
    with open( args.ct ) as f:
        n_fields = len(f.readline().split())

    if n_fields == nLabels + 1:
        # attempt to read as a scoring-only pseudo-image-table
        computed_it = ImageTable()
        with open( args.ct ) as f:
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
        computed_it = ImageTable.read_from_file( args.ct )

    sys.stderr.write('Info: read %d computed entries\n' % len(computed_it.entries ))

    if args.r is not None:
        if args.r == 'b':
            sys.stderr.write('Replacing computed answers with random 50/50 yes/no results...\n')
            for (k, e) in computed_it.entries.iteritems():
                for i in range(0, len(e.label_vector)):
                    e.label_vector[i] = random.choice( [-1, 1] )

        elif args.r == 'p':
            sys.stderr.write('Replacing computed answers with random yes/no results based on truth priors...\n')
            # compute priors
            counts = [0] * nLabels
            for (k, e) in true_it.entries.iteritems():
                for i in range(0, len(e.label_vector)):
                    if e.label_vector[i] == 1:
                        counts[i] += 1
            nOpportunities = len(computed_it.entries)
            for (k, e) in computed_it.entries.iteritems():
                for i in range(0, len(e.label_vector)):
                    v = random.randint(0, nOpportunities)
                    e.label_vector[i] = 1 if v < counts[i] else -1
        else:
            raise AssertionError('Logic error: unexpected "-r" argument %s' % args.r )


    with open( args.tht ) as f:
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
    sys.stdout.write('"index","label","AP","n-predictions","BER","n-instances","n-correct","%-correct","n-true-pos","n-est-pos-correct","pD","n-est-pos-wrong","n-true-neg","n-est-neg-correct","n-est-neg-wrong","FPR","FNR"\n')

    avgprecList = []

    for i in range(0, nLabels):
        # create mapping from computed score to correct/incorrect
        # ...need to allow for duplicate score values! Python doesn't seem
        # to have a native multimap :(

        t = threshold_table[i]
        score_map = dict()  # key: image_id, val: score
        correct_map = dict() # key: image_id, val: True if correct, False if not -- this is NOT the "relevant" table used for AP
        relevant_map = dict() # key: image_id, val: True is label is set, False if not

        (n_instances, n_true_pos, n_predicted_pos_correct, n_predicted_pos_wrong, n_true_neg, n_predicted_neg_correct, n_predicted_neg_wrong) = (0,0,0,0,0,0,0)

        for (image_id, true_image_entry) in true_it.entries.iteritems():
            if image_id_state_map[ image_id ] != 0x03:
                continue
            s = computed_it.entries[ image_id ].label_vector[ i ]
            r = true_image_entry.label_vector[ i ]
            relevant_map[ image_id ] = r
            if r == -1:
                # don't score this label; skip
                continue

            n_instances += 1
            score_map[ image_id ] = s

            if  r == 1:
                n_true_pos += 1
                result = (s >= t)
                if result:
                    # truth is 1, result is 1: got it!
                    n_predicted_pos_correct += 1
                else:
                    # truth is 1, result is 0: false negative
                    n_predicted_neg_wrong += 1
            elif r == 0:
                n_true_neg += 1
                result = (s < t)
                if result:
                    # truth is 0, result is 0: got it!
                    n_predicted_neg_correct += 1
                else:
                    # truth is 0, result is 1: false positive
                    n_predicted_pos_wrong += 1
            else:
                raise AssertionError( 'Image %d label %d: unexpected label vector value %f\n' % (image_id, i, r))

            correct_map[ image_id ] = result

        if n_instances == 0:
            sys.stderr.write('Skipping label %d: %s\n'% (i,lt.id2label[i]))
            continue

        avgprec, n_predictions = calculate_AP( relevant_map, score_map )
        avgprecList.append(avgprec)

        n_correct_total = correct_map.values().count( True )

        sys.stdout.write('%d,%s,' % (i, lt.id2label[i]))
        sys.stdout.write('%0.5f,%d,' % (avgprec, n_predictions) )
        false_positive_rate = 1.0 * n_predicted_pos_wrong / n_true_neg
        false_negative_rate = 1.0 * n_predicted_neg_wrong / n_true_pos
        ber = (false_positive_rate + false_negative_rate) / 2.0
        sys.stdout.write('%0.5f,' % ber )
        sys.stdout.write('%d,%d,%0.5f,' % (n_instances, n_correct_total, 1.0*n_correct_total/n_instances))
        sys.stdout.write('%d,%d,%0.5f,%d,' % (n_true_pos, n_predicted_pos_correct, 1.0*n_predicted_pos_correct / n_true_pos,n_predicted_pos_wrong ))
        sys.stdout.write('%d,%d,%d,' % (n_true_neg, n_predicted_neg_correct,n_predicted_neg_wrong))
        sys.stdout.write('%0.5f,%0.5f'% (false_positive_rate, false_negative_rate))
        sys.stdout.write('\n')

    meanavgprec = mean(avgprecList)
    sys.stderr.write('Info: mAP: %f\n ' % meanavgprec)
    if -1 in avgprecList:
        sys.stderr.write('\nWarning: one of the APs returned -1. This means there were no actual positives for that label.')


if __name__ == "__main__":
    main()
