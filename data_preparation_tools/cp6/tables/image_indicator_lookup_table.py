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
## implement the image indicator lookup table
##

import sys
from cp6.utilities.util import Util
from cp6.utilities.image_indicator import ImageIndicator, ImageIndicatorEntry

class ImageIndicatorLookupTable:

    def __init__( self ):
        self.groups = dict()  # key: text; val: ImageIndicatorEntry
        self.words = dict()   # key: text; val: ImageIndicatorEntry
        self.groups_index = dict() # key: id; val: ImageIndicatorEntry
        self.words_index = dict()  # key: id; val; ImageIndicatorEntry

    def set_from_mcauley( self, fn, stopwords_fn ):
        stopwords = dict()
        with open( stopwords_fn ) as f:
            while 1:
                stopword = f.readline()
                if not stopword:
                    break
                stopword = stopword.strip()
                stopwords[ stopword ] = True
        sys.stderr.write('Info: read %d stopwords\n' % len(stopwords))

        n_stopwords_found = 0
        with open( fn ) as f:
            header_fields = f.readline().strip().split()
            if len(header_fields) != 3:
                raise AssertionError( 'Found %d fields in header of %s; expecting 3\n' % \
                                      ( len(header_fields), fn ))
            (n_groups, n_tags, n_labels) = \
              (int(header_fields[0]), int(header_fields[1]), int(header_fields[2]))

            for index in range( 0, n_groups ):
                raw_line = f.readline()
                if not raw_line:
                    raise AssertionError( 'Failed to read group line %d in %s\n' % \
                                          (index, fn ) )
                fields = raw_line.strip().split()
                if len(fields) != 2:
                    raise AssertionError( 'Found %d fields in group line "%s"; expecting 2\n' % \
                                          (len(fields), raw_line.strip()))
                self.groups[ fields[1] ] = ImageIndicatorEntry( index, 'G', fields[1] )
                self.groups_index[ index ] = ImageIndicatorEntry( index, 'G', fields[1] )

            index = 0
            for i in range( 0, n_tags ):
                raw_line = f.readline()
                if not raw_line:
                    raise AssertionError( 'Failed to read tag line %d in %s\n' % \
                                          (index, fn ) )
                fields = raw_line.strip().split()
                if len(fields) != 2:
                    raise AssertionError( 'Found %d fields in tag line "%s"; expecting 2\n' % \
                                          (len(fields), raw_line.strip()))

                if fields[1] in stopwords:
                    n_stopwords_found += 1
                else:
                    self.words[ fields[1] ] = ImageIndicatorEntry( index, 'W', fields[1] )
                    self.words_index[ index ] = ImageIndicatorEntry( index, 'W', fields[1] )
                    index += 1
        sys.stderr.write('Info: Found %d stopwords reading LUT\n' % n_stopwords_found)

    def init_indicator( self, id ):
        imgind = ImageIndicator( id )
        imgind.group_list = dict()
        imgind.word_list = dict()
        imgind.word_source_flags = dict()
        return imgind

    def add_to_indicator( self, imgind, ind_type, new_text, source_flag ):
        if not new_text:
            return
        for word in new_text.split():
            if ind_type == 'G':
                if word in self.groups:
                    imgind.group_list[ self.groups[word].id ] = True
            elif ind_type == 'W':
                if word in self.words:
                    index = self.words[word].id
                    if not index in imgind.word_list:
                        imgind.word_source_flags[ index ] = ImageIndicator.IN_NONE
                    imgind.word_list[ index ] = True
                    imgind.word_source_flags[ index ] |= source_flag
            else:
                raise AssertionError( 'Bad indicator type %s\n' % ind_type )

    def write_to_file( self, fn ):
        with open( fn, 'w' ) as f:
            f.write( '%d %d\n' % (len(self.groups), len(self.words)))
            for i in range(0, len(self.groups)):
                ind = self.groups_index[ i ]
                f.write( '%d %s %s %d\n' \
                         % (ind.id, ind.type, Util.qstr( ind.s ), ImageIndicator.IN_NONE ))
            for i in range(0, len(self.words)):
                ind = self.words_index[ i ]
                f.write( '%d %s %s %d\n' \
                         % (ind.id, ind.type, Util.qstr( ind.s ), self.word_source_flags[ ind.id ]))

    @staticmethod
    def read_from_file( fn ):
        t = ImageIndicatorLookupTable()
        with open( fn, 'r' ) as f:
            header_fields = Util.qstr_split( f.readline() )
            if len(header_fields) != 2:
                raise AssertionError( 'ImageIndicatorLookupTable "%s": header had %d fields, expected 2' % \
                                      ( fn, len(header_fields)))
            (n_groups, n_words) = map(int, header_fields)
            for i in range(0, n_groups):
                group_fields = Util.qstr_split( f.readline() )
                if len(group_fields) != 4:
                    raise AssertionError( 'ImageIndicatorLookupTable "%s": group %d had %d fields, expected 4' % \
                                          (fn, i, len(group_fields)))
                e = ImageIndicatorEntry( int(group_fields[0]), group_fields[1], group_fields[2])
                t.groups_index[ e.id ] = e
                t.groups[ e.s ] = e
            for i in range(0, n_words):
                word_fields = Util.qstr_split( f.readline() )
                if len(word_fields) != 4:
                    raise AssertionError( 'ImageIndicatorLookupTable "%s": word %d had %d fields, expected 4' % \
                                          (fn, i, len(word_fields)))
                e = ImageIndicatorEntry( int(word_fields[0]), word_fields[1], word_fields[2] )
                t.words_index[ e.id ] = e
                t.words[ e.s ] = e


        return t

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: $0 input-img-indicator-table output-img-indicator-table\n')
        sys.exit(0)
    t = ImageIndicatorTable.read_from_file( sys.argv[1] )
    sys.stderr.write('Info: image indicator table has %d grops and %d words\n' \
                     % (len(t.groups), len(t.words)))
    t.write_to_file( sys.argv[2] )
