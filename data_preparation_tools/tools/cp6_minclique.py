# Copyright 2016 Kitware, Inc.
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

#
# Examine label overlap within an image table.
#
# With 3 arguments, examine the N-way overlap between labels, printing
# a metric of how much each set of N-combinations of labels overlap.
#
# With 4 arguments, the fourth is a comma-separated list of label IDs.
# Print out the image IDs which have labels in the list.
#

import sys
import os
import itertools

from cp6.tables.image_table import ImageTable
from cp6.tables.label_table import LabelTable

if __name__ == '__main__':

    if len(sys.argv) not in [4, 5]:
        sys.stderr.write( 'Usage: $0 label_table image_table N [label1,label2,label3,...]\n' )
        sys.exit(0)

    (lt_fn, it_fn, n_clique) = (sys.argv[1], sys.argv[2], int(sys.argv[3]))
    lt = LabelTable.read_from_file( lt_fn )
    it = ImageTable.read_from_file( it_fn )

    selected_set = list()
    if len(sys.argv) == 5:
        selected_set = [int(s) for s in sys.argv[4].split(',')]

    nLabels = len(lt.idset)
    confusion = [ [0 for x in range(nLabels)] for y in range(nLabels)]
    for (id, e) in it.entries.iteritems():
        if len(selected_set) > 0:
            hits = [index for index in selected_set if e.label_vector[index]==1]
            if len(hits) > 0:
                print id, ' '.join(str(i) for i in hits)

        labels = [index for index in range(nLabels) if e.label_vector[index]==1]
        for x in labels:
            confusion[x][x] += 1
        for (x,y) in list(itertools.combinations( labels, 2 )):
            confusion[x][y] += 1

    min_required_count = 75;
    for c in list( itertools.combinations( range(nLabels), n_clique ) ):
        keep = True
        for i in c:
            if confusion[i][i] < min_required_count:
                keep = False
        if not keep:
            continue

        sum = 0
        report = list()
        for (x,y) in list(itertools.combinations( c, 2)):
            factor = 1.0 * confusion[x][y] / (confusion[x][x] + confusion[y][y])
            sum += factor
            report.append('%d:%d = %d/%d (%f)' % (x, y, confusion[x][y], confusion[x][x]+confusion[y][y], factor))

        names = ['%s(%d):%d' % (lt.id2label[i], i, confusion[i][i]) for i in c]
        if len(selected_set) == 0:
            print sum, names, report
