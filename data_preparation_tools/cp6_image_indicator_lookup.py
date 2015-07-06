##
## implement the image indicator lookup table
##

import sys
from cp6_util import CP6Util


class CP6ImageIndicatorEntry:
    def __init__( self, id, t, s ):
        self.id = id
        self.type = t  # 'G' for group, 'W' for word
        self.s = s

class CP6ImageIndicator:
    (IN_NONE, IN_TITLE, IN_DESC, IN_TAG, IN_COMMENT) = (0x0,0x01,0x02,0x04,0x08)
    def __init__( self, id ):
        self.id = id
        self.group_list = None
        self.word_list = None
        self.word_source_flags = None

    def __str__( self ):
        return 'imageindicator %d: %d groups, %d words' % \
          (self.id, len(self.group_list), len(self.word_list))

class CP6ImageIndicatorLookupTable:

    def __init__( self, fn, stopwords_fn ):
        self.stopwords = dict()
        with open( stopwords_fn ) as f:
            while 1:
                stopword = f.readline()
                if not stopword:
                    break
                stopword = stopword.strip()
                self.stopwords[ stopword ] = True
        sys.stderr.write('Info: read %d stopwords\n' % len(self.stopwords))

        self.groups = dict()  # key: text; val: CP6ImageIndicatorEntry
        self.words = dict()   # key: text; val: CP6ImageIndicatorEntry
        self.groups_index = dict() # key: id; val: CP6ImageIndicatorEntry
        self.words_index = dict()  # key: id; val; CP6ImageIndicatorEntry
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
                self.groups[ fields[1] ] = CP6ImageIndicatorEntry( index, 'G', fields[1] )
                self.groups_index[ index ] = CP6ImageIndicatorEntry( index, 'G', fields[1] )

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

                if fields[1] in self.stopwords:
                    n_stopwords_found += 1
                else:
                    self.words[ fields[1] ] = CP6ImageIndicatorEntry( index, 'W', fields[1] )
                    self.words_index[ index ] = CP6ImageIndicatorEntry( index, 'W', fields[1] )
                    index += 1
        sys.stderr.write('Info: Found %d stopwords reading LUT\n' % n_stopwords_found)

    def write_image_indicator_lookup_table( self, fn ):
        with open( fn, 'w' ) as f:
            f.write( '%d %d\n' % (len(self.groups), len(self.words)))
            for i in range(0, len(self.groups)):
                ind = self.groups_index[ i ]
                f.write( '%d %s %s\n' % (ind.id, ind.type, CP6Util.qstr( ind.s )))
            for i in range(0, len(self.words)):
                ind = self.words_index[ i ]
                f.write( '%d %s %s\n' % (ind.id, ind.type, CP6Util.qstr( ind.s )))

    def init_indicator( self, id ):
        imgind = CP6ImageIndicator( id )
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
                        imgind.word_source_flags[ index ] = CP6ImageIndicator.IN_NONE
                    imgind.word_list[ index ] = True
                    imgind.word_source_flags[ index ] |= source_flag
            else:
                raise AssertionError( 'Bad indicator type %s\n' % ind_type )

