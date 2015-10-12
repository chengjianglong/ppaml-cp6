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
from cp6.utilities.image_indicator import ImageIndicator

##
## This is a little convoluted.
##
## The IILUT's first job is to match numeric (entry) IDs to
## ImageIndicatorEntry objects. However, during construction from
## McAuley's XML, it's convenient to be able to lookup up an IIE
## using the source text, not the ID.
##
## Note that these IDs are the IILUT entry IDs, not the image IDs.
## From here we have no way of knowing what images reference these
## entries.
##


class ImageIndicatorEntry:
    #
    # One of these per entry in the IILUT.
    def __init__( self, id, t, s ):
        #
        # id: IILUT id, not an image ID.
        # t: 'G' for group, 'W' for word.
        # s: the text of the entry.
        #
        self.id = id
        self.type = t
        self.s = s

class ImageIndicatorLookupTable:

    def __init__( self ):
        self.group_table = dict()    # key: id; val: IIE
        self.word_table = dict()     # key: id; val: IIE
        self.group_text_lut = dict() # key: text, val: group_table ID
        self.word_text_lut = dict() # key: text, val: word_table ID

#x        self.groups = dict()  # key: text; val: ImageIndicatorEntry
#x        self.words = dict()   # key: text; val: ImageIndicatorEntry
#x        self.groups_index = dict() # key: id; val: ImageIndicatorEntry
#x        self.words_index = dict()  # key: id; val; ImageIndicatorEntry

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

            #
            # set the groups
            #

            for index in range( 0, n_groups ):
                raw_line = f.readline()
                if not raw_line:
                    raise AssertionError( 'Failed to read group line %d in %s\n' % \
                                          (index, fn ) )
                fields = raw_line.strip().split()
                if len(fields) != 2:
                    raise AssertionError( 'Found %d fields in group line "%s"; expecting 2\n' % \
                                          (len(fields), raw_line.strip()))
                self.group_table[ index ] = ImageIndicatorEntry( index, 'G', fields[1] )
                self.group_text_lut[ fields[1] = index
#x                self.groups[ fields[1] ] = ImageIndicatorEntry( index, 'G', fields[1] )
#x                self.groups_index[ index ] = ImageIndicatorEntry( index, 'G', fields[1] )

            #
            # set the words
            #

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
                    self.word_table[ index ] = ImageIndicatorEntry( index, 'W', fields[1] )
                    self.word_text_lut[ fields[1] ] = index
#x                    self.words[ fields[1] ] = ImageIndicatorEntry( index, 'W', fields[1] )
#x                    self.words_index[ index ] = ImageIndicatorEntry( index, 'W', fields[1] )
                    index += 1
        sys.stderr.write('Info: Found %d stopwords reading LUT\n' % n_stopwords_found)

#x    def init_indicator( self, id ):
#x        imgind = ImageIndicator( id )
#x        imgind.group_list = dict()
#x        imgind.word_list = dict()
#x        imgind.word_source_flags = dict()
#x        return imgind

    def add_to_indicator( self, imgind, ind_type, new_text, source_flag ):
        #
        # Given the existing image indicator imgind, look up the words in
        # new_text in the appropriate {group,word}_table. If present, record
        # it in imgind.
        #
        # groups have no 'source', they're just from groups. (If we recorded
        # the various flavors of flickr groups-- albums vs. galleries, etc-- it
        # would go here.)
        #
        # words have various sources (enumerated in the ImageIndicator flags).
        # We don't histogram how often they occur, we just flip the bits.
        #

        if not new_text:
            return
        for word in new_text.split():

            if ind_type == 'G':
                if word in self.group_text_lut:
                    entry_id = self.group_text_lut[ word ]
                    imgind.group_list[ entry_id ] = True

            elif ind_type == 'W':
                if word in self.word_text_lut:
                    entry_id = self.group_text_lut[ word ]
                    if not entry_id in imgind.word_list:
                        imgind.word_source_flags[ entry_id ] = ImageIndicator.IN_NONE
                    imgind.word_list[ entry_id ] = True
                    imgind.word_source_flags[ entry_id ] |= source_flag

            else:
                raise AssertionError( 'Bad indicator type %s\n' % ind_type )

    def write_to_file( self, fn ):
        with open( fn, 'w' ) as f:
            f.write( '%d %d\n' % (len(self.group_text_lut), len(self.word_text_lut)))
            for i in sorted( self.group_text_lut.iteritems(), key=lamdba x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d G %s\n', entry_id, Util.qstr( entry_text ))
            for i in sorted( self.group_word_lut.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d W %s\n', entry_id, Util.qstr( entry_text ))

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
                fields = Util.qstr_split( f.readline() )
                if len(fields) != 3:
                    raise AssertionError( 'ImageIndicatorLookupTable "%s": group %d had %d fields, expected 3' % \
                                          (fn, i, len(fields)))
                if fields[1] != 'G':
                    raise AssertionError( 'ImageIndicatorLookupTable "%s": entry %d flavor was %s; expected "G"' % \
                                          (fn, i, fields[1]))

                t.group_lext_lut[ fields[2] ] = int( fields[0] )

            for i in range(0, n_words):
                fields = Util.qstr_split( f.readline() )
                if len(fields) != 3:
                    raise AssertionError( 'ImageIndicatorLookupTable "%s": word %d had %d fields, expected 3' % \
                                          (fn, i, len(word_fields)))
                if fields[1] != 'W':
                    raise AssertionError( 'ImageIndicatorLookupTable "%s": entry %d flavor was %s; expected "W"' % \
                                          (fn, i, fields[1]))

                t.word_text_lut[ fields[2] ] = int( fields[0] )

        return t

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: $0 input-img-indicator-table output-img-indicator-table\n')
        sys.exit(0)
    t = ImageIndicatorTable.read_from_file( sys.argv[1] )
    sys.stderr.write('Info: image indicator table has %d grops and %d words\n' \
                     % (len(t.groups), len(t.words)))
    t.write_to_file( sys.argv[2] )
