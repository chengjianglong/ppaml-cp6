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
## handy methods
##

import sys
from collections import defaultdict

from cp6.util.paths import CP6Paths, CP6PhaseTable

class CP6Util:

    @staticmethod
    def qstr( s ):
        if not s:
            return 'none'

        s = s.replace( '"',' ' ).replace( '\n', ' ').replace( '\r', ' ' )
        return ( '"%s"' % s ).encode( "UTF-8" )

    @staticmethod
    def qstr_split( s ):
        words = list()
        current_word = ''
        in_quote = False
        for i in range(0, len(s)):
            is_quote = (s[i] == '"')
            if in_quote:
                if is_quote:
                    words.append(current_word)
                    current_word = ''
                    in_quote = False
                else:
                    current_word += s[i]
            else:
                if is_quote:
                    in_quote = True
                elif (s[i] == ' ') or (s[i] == '\t'):
                    if len(current_word):
                        words.append(current_word)
                        current_word = ''
                else:
                    current_word += s[i]
        if len(current_word):
            words.append( current_word )
        if in_quote:
            sys.stderr.write('WARN: unbalanced quotes in \'%s\'\n' % s)
        return words

    @staticmethod
    def exercise_qstr_split():
        for s in ['', \
                  'a', '  a', 'a  ','  a  ', \
                  'aa bb', '  aa bb', 'aa    bb', 'aa  bb  ','  aa  bb  ',\
                  'a b c', ' a b c ', 'a    b c ', \
                  '""', 'a "b c" d', '"a" b c', ' "a " b c ', '"a ""b " "c" ', '"a""b""c"', \
                  'a b "c d""e f"', ' a b d "e' ]:
            sys.stderr.write('TEST: input \'%s\'\n' % s)
            words = CP6Util.qstr_split(s)
            for i in range(0, len(words)):
                sys.stderr.write('TEST: output %d / %d: \'%s\'\n' % (i, len(words), words[i]))


    @staticmethod
    def read_label_table( fn ):
        id2label = dict()
        label2id = dict()
        with open(fn) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                fields = CP6Util.qstr_split( raw_line )
                id2label[ int(fields[0]) ] = fields[1]
                label2id[ fields[1] ] = int(fields[0])
        return (id2label, label2id)

    @staticmethod
    def count_labels_in_image_table( fn, flag_to_count = 1 ):
        label_vector_count = defaultdict(int)
        with open( fn ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                fields = CP6Util.qstr_split( raw_line )
                if len(fields) != 10:
                    raise AssertionError("Expected 10 fields in '%s', found %d\n" % (raw_line, len(fields)))
                for (ind, val) in enumerate( fields[9].split(',')):
                    if int(val) == flag_to_count:
                        label_vector_count[ ind ] += 1
        return label_vector_count

    @staticmethod
    def node_ids_with_label_in_image_table( fn, label_index, flag_to_count = 1 ):
        node_ids = list()
        with open( fn ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                fields = CP6Util.qstr_split( raw_line )
                if len(fields) != 10:
                    raise AssertionError("Expected 10 fields in '%s', found %d\n" % (raw_line, len(fields)))
                labels = map(int, fields[9].split(','))
                if labels[ label_index ] == flag_to_count:
                    node_ids.append( int(fields[0]) )
        return node_ids


    @staticmethod
    def label_census( paths, phase_key ):
        (id2label, label2id) = CP6Util.read_label_table( paths.label_table_path )
        label_vector_count = CP6Util.count_labels_in_image_table( paths.phase_tables[phase_key].image_table )
        for ind in label_vector_count:
            sys.stdout.write('Info: label "%s" appears %d times\n' % (id2label[ind], label_vector_count[ind]))

    @staticmethod
    def nodes_with_label( paths, phase_key, label_string ):
        (id2label, label2id) = CP6Util.read_label_table( paths.label_table_path )
        nodes = CP6Util.node_ids_with_label_in_image_table( paths.phase_tables[phase_key].image_table, label2id[label_string])
        return nodes


if __name__ == '__main__':
    # CP6Util.label_census( CP6Paths(), 'r1train')
    CP6Util.nodes_with_label( CP6Paths(), 'r1train', 'sea')



