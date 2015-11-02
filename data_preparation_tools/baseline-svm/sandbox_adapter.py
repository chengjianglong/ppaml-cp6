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

import os
import sys

from cp6.tables.image_table import ImageTable
from cp6.tables.image_indicator_table import ImageIndicatorTable
from cp6.tables.image_indicator_lookup_table import ImageIndicatorLookupTable
from cp6.tables.label_table import LabelTable
from cp6.tables.edge_table import EdgeTable
from cp6.utilities.image_edge import ImageEdge

class SandboxAdapter:

    def __init__( self, sandbox_root ):
        self.files = dict()
        self.files[ 'lt' ] = os.path.join( sandbox_root, 'eval_in', 'etc', 'label_table.txt' )
        self.files[ 'iilut' ] = os.path.join( sandbox_root, 'eval_in', 'etc', 'image_indicator_lookup_table.txt' )

        self.files[ 'train-it' ] = os.path.join( sandbox_root, 'run_in', 'training', 'image_table.txt' )
        self.files[ 'test-it' ] = os.path.join( sandbox_root, 'run_in', 'testing', 'image_table.txt' )
        self.files[ 'answer-it' ] = os.path.join( sandbox_root, 'eval_in', 'testing', 'image_table.txt' )

        self.files[ 'train-iit' ] = os.path.join( sandbox_root, 'run_in', 'training', 'image_indicator_table.txt' )
        self.files[ 'test-iit' ] = os.path.join( sandbox_root, 'run_in', 'testing', 'image_indicator_table.txt' )

        self.files[ 'train-et' ] = os.path.join( sandbox_root, 'run_in', 'training', 'image_edge_table.txt' )
        self.files[ 'test-et' ] = os.path.join( sandbox_root, 'run_in', 'testing', 'image_edge_table.txt' )

        for (k,v) in self.files.iteritems():
            if not os.path.isfile( v ):
                raise AssertionError( 'Expected file %s (tag %s) is not present\n' % (v,k))

    @staticmethod
    def write_node_features( fn, ii_lookup_table, label_table, \
                             image_table, image_indicator_table ):
        #
        # node features are read starting at genericdata.cpp:188.
        #
        # The nodeFeatures file has the following layout:
        #
        # [1] nGroups nTags nLabels
        # [2] group_id group_name
        # [3] tag_id tag_name
        # [4] label_id label_name
        # [5] nPhotos
        # [6] photo_id user_id indicator
        #
        # Multiplicities:
        #
        # [1] x 1
        # [2] x nGroups
        # [3] x nTags
        # [4] x nLabels
        # [5] x 1
        # [6] x nPhotos
        #
        # [2] and [3] are from our ImageIndicatorLookupTable. [4] is
        # our label table (I think.) [6] can be (cp6_id, fake_user,
        # indicator), where indicator is a string of length
        # nGroups+nTags+nLabels. Each character is either '.', '0', or
        # '1'.  Looking at genericdata.cpp:284, chars are either '1'
        # or not '1' for groups and tags. Labels are '0' if negative,
        # '1' if positive.
        #
        # Note that group_id, tag_id, label_id are all sequential:
        # the first tag_id is the last group_id + 1.
        #
        # Note also that these aren't the word features.
        #

        with open(fn, 'w') as f:

            # write the header line [1]

            nGroups = len( ii_lookup_table.group_text_lut )
            nTags = sum(1 for x in ii_lookup_table.tag_word_text_src.values() if ((x == 'T') or ( x == 'B')))
            nLabels = len( label_table.label2id )
            f.write('%d %d %d\n' % ( nGroups, nTags, nLabels ))

            c = 0

            # write the group lines [2]

            for i in sorted( ii_lookup_table.group_text_lut.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d %s\n' % ( c, entry_text ))
                c += 1

            # write the tag lines [3] .. not sure how McAuley's code handles UTF-8?
            emitted_tag_ids = list()
            for i in sorted( [v for k,v in ii_lookup_table.tag_word_text_lut.iteritems() if ii_lookup_table.tag_word_text_src[v] in ['T','B']]):
                (entry_id, entry_text) = (v, k)
                f.write( '%d %s\n' % ( c, entry_text ))
                emitted_tag_ids.append( entry_id )
                c += 1

            if len(emitted_tag_ids) != nTags:
                raise AssertionError('Expected to emit %d tags but only wrote %d\n' %\
                                     (nTags, len(emitted_tag_ids)))
            # write the label lines [4]

            for i in sorted( label_table.label2id.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d %s\n' % (c, entry_text ))
                c += 1

            # write the header line [5]

            nImages = len( image_table.entries )
            f.write('%d\n' % nImages )

            # write the image indicator lines [6]

            for i in sorted( image_table.entries.iteritems(), key=lambda x:x[1] ):
                (img_id, user) = (i[1].mir_id, i[1].flickr_owner)
                ii = image_indicator_table.image_indicators[ img_id ]
                s = ''
                for i in range(0, nGroups):
                    if i in ii.group_list:
                        s += '1'
                    else:
                        s += '.'
                for i in range(0, nTags):
                    if emitted_tag_ids[i] in ii.word_list:
                        s += '1'
                    else:
                        s += '.'
                lv = image_table.entries[ img_id ].label_vector
                for i in range(0, nLabels):
                    v = lv[i]
                    if v == 1:
                        s += '1'
                    elif v == 0:
                        s += '0'
                    else:
                        s += '.'
                f.write('%d %s %s\n' %( img_id, user, s ))

            # all done

    @staticmethod
    def write_edge_features( fn, edge_table ):
        # #
        # # edgeFeatures, trainingEdgeFeatures:
        # # genericdata.cpp:450
        # #
        #
        #
        # [1] nEdges nEdgeFeatures
        # [2] img_id_1 img_id_2 feature-list
        #
        # Multiplicities:
        #
        # [1] x 1
        # [2] x nEdges
        #
        # The feature-list, from McAuley page 10:
        #
        # nTags nGroups nCollections nGalleries flagLoc flUser flFriend
        #
        # n{Tags,Groups,Collections}: "The number of common tags, groups, collections, and galleries"
        #
        # flLoc: "An indicator for whether both photos were taken in the same
        # location (GPS coordinates are organized into distinct 'localities' by
        # Flickr)"
        #
        # flUser: "An indicator for whether both photos were taken by the same user"
        #
        # flFriend: "An indicator for whether both photos were taken by contacts/friends"
        #
        # Example (edgeFeaturesPASCAL.txt), syntax: {label} (line-number) payload
        #
        # {a} (1) 2684742 7
        # {b} (2) 106998777 15256584 0 2 0 0 0 0 0
        # {c} (2684743) 2110031507 1116386773 0 1 0 0 0 0 0
        #
        # ...so:
        #
        # {a} is 1 x [1]
        # {b}..{c} is 2684742 x [2]
        #
        # We don't record collections or galleries, only groups.
        #

        with open(fn, 'w') as f:

            # write the header line [1]

            f.write('%d 7\n' % len( edge_table.edges ))  # always write seven features

            # write the edges [2]

            for e in edge_table.edges:
                f.write('%d %d ' % (e.image_A_id, e.image_B_id))
                f.write('%d %d 0 0 ' % (len(e.shared_words), len(e.shared_groups)))
                f.write('%d %d %d\n' % (ImageEdge.canonical_flag_int( e.same_location_flag ), \
                                       ImageEdge.canonical_flag_int( e.same_user_flag ), \
                                       ImageEdge.canonical_flag_int( e.shared_contact_flag )))

            # all done

    @staticmethod
    def write_text_features( fn, image_table, image_indicator_table, iilut ):
        #
        # Use of this file is controlled by the nodeFeatures flag, but
        # this is the only place the textFile variable is referenced.
        #
        # from genericdata.cpp:292: nWords is set, and nWords are parsed but
        # discarded. Then nPhotos are loaded, each line (:310) is:
        #
        # photoID userID nFeatures {nFeatures x '%d:%d'}
        #
        # ...where (key,val) = %d:%d are:
        #
        # ...... key is the index of the word-to-use
        #
        # ...... val is an int multiplied by 1/nwords (:326).
        # ...... For the pascal examples, val is always '1'.
        # ...... Also always '1' in trainingTextMIR.txt.
        #
        # These are read into the nodeFeatures array (see :316) at the
        # offset after the imagefeatures, groups, and tags are read.
        #
        #
        # so the file we write is:
        #
        #
        # [1] nwords
        # [2] word
        # [3] photoID userID nFeatures {nFeatures x '%d:1'}
        #
        # [1] x 1
        # [2] x nwords
        # [3] x nPhotos from node features file
        #
        # ...the features in [3] are *words*, not tags.
        #
        # Interestingly, [1] and [2] are discarded, so we can minimize them here.
        #
        #

        with open(fn, 'w') as f:

            # write a fake [1] and [2]

            f.write( '1\n' )
            f.write( '0 this_word_is_not_used\n' )

            # write [3]

            for i in sorted( image_table.entries.iteritems(), key=lambda x:x[1] ):
                (img_id, user) = (i[1].mir_id, i[1].flickr_owner)

                # how many IILUT entries of type 'W' or 'B' are we looking for?
                ii = image_indicator_table.image_indicators[ img_id ]
                wb_list = [i for i in ii.word_list.keys() if (iilut.tag_word_text_src[i] in ['W','B'])]
                n = len(wb_list)
                f.write('%d %s %d ' % (img_id, user, n))
                for j in wb_list:
                    f.write('%d:1 ' % j )
                f.write('\n')
            # all done

    @staticmethod
    def write_id_file( fn, image_table, image_indicator_table, iilut ):
        #
        # genericdata.cpp:80 ... this is the "group ID" file (training only)
        #
        # [1] label_id
        # [2] name nGroups nTags
        # [3] groupID:flag (%d:%f)
        # [4] tagID:flag (%d:%f)
        #
        # ...[1], [2], [3], [4] repeated for each label. Within each label, [3]
        # repeated for each group associated with the label. flag value
        # needs to be >2. Ditto [4], repeated for each tag (word) associated with
        # the label.
        #
        # We reconstruct this by first building a label-to-image list, then
        # for each label, flagging the groups associated with the images.
        # Ditto for tags.
        #

        label2group = dict()  # key: label ID; val: set of group IDs
        label2tag = dict()   # key: label ID; val: set of tag IDs

        for (img_id, img) in image_table.entries.iteritems():
            ii = image_indicator_table.image_indicators[ img_id ]
            lv = img.label_vector

            if len(label2group) == 0:
                for i in range(0,len(lv)):
                    label2group[i] = set()
                    label2tag[i] = set()

            for label_index in range(0, len(lv)):
                if lv[label_index] != 1:
                    continue
                # we now know that img_id is associated with label_index
                # (assumes label_index == label_id, hmm)
                for i in ii.group_list.iteritems():
                    label2group[label_index].add( i[0] )
                for i in ii.word_list.iteritems():
                    if iilut.tag_word_text_src[i[0]] in ['T','B']:
                        label2tag[label_index].add( i[0] )

        with open(fn, 'w') as f:
            for i in sorted( label2group.iteritems(), key=lambda x:x[1] ):
                label_index = i[0]
                (g, t) = (label2group[label_index], label2tag[label_index])
                f.write('%d labelname-not-used %d %d ' % (i[0], len(g), len(t)))
                for j in g:
                    f.write('%d:3 ' % j)
                for j in t:
                    f.write('%d:3 ' % j)
                f.write('\n')

        # all done

    @staticmethod
    def write_text_id_file( fn, image_table, image_indicator_table, iilut ):
        #
        # genericdata.cpp:145
        #
        # [1] label_id
        # [2] name nWords
        # [3] wordID:flag (%d:%f)
        #
        # ...[1], [2], [3] repeated for each label. Within each label, [3]
        # repeated for each word associated with the label. flag value
        # needs to be >2.

        label2word = dict()   # key: label ID; val: set of word IDs

        for (img_id, img) in image_table.entries.iteritems():
            ii = image_indicator_table.image_indicators[ img_id ]
            lv = img.label_vector

            if len(label2word) == 0:
                for i in range(0,len(lv)):
                    label2word[i] = set()

            for label_index in range(0, len(lv)):
                if lv[label_index] != 1:
                    continue
                # we now know that img_id is associated with label_index
                # (assumes label_index == label_id, hmm)
                for i in ii.word_list.iteritems():
                    if iilut.tag_word_text_src[i[0]] in ['W']:
                        label2word[label_index].add( i[0] )

        with open(fn, 'w') as f:
            for i in sorted( label2word.iteritems(), key=lambda x:x[1] ):
                label_index = i[0]
                w = label2word[label_index]
                f.write('%d labelname-not-used %d ' % (i[0], len(w)))
                for j in w:
                    f.write('%d:3 ' % j)
                f.write('\n')

        # all done

    def load( self ):
        self.lt = LabelTable.read_from_file( self.files['lt'] )
        sys.stderr.write('Info: loaded label table\n')
        self.iilut = ImageIndicatorLookupTable.read_from_file( self.files['iilut'] )
        if not self.iilut.verify():
            sys.stderr.write('Exiting\n')
            sys.exit(1)
        sys.stderr.write('Info: loaded and verified image indicator lookup table\n')
        self.train_it = ImageTable.read_from_file( self.files[ 'train-it' ] )
        sys.stderr.write('Info: loaded training image table\n' )
        self.test_it = ImageTable.read_from_file( self.files[ 'test-it' ] )
        sys.stderr.write('Info: loaded testing image table\n' )
        self.train_iit = ImageIndicatorTable.read_from_file( self.files[ 'train-iit'] )
        sys.stderr.write('Info: loaded training image indicator table\n' )
        self.test_iit = ImageIndicatorTable.read_from_file( self.files[ 'test-iit'] )
        sys.stderr.write('Info: loaded testing image indicator table\n' )
        self.train_et = EdgeTable.read_from_file( self.files[ 'train-et' ] )
        sys.stderr.write('Info: loaded training edge table\n')
        self.test_et = EdgeTable.read_from_file( self.files[ 'test-et' ] )
        sys.stderr.write('Info: loaded testing edge table\n')

    def write( self, out_dir ):
        outfiles = dict()

        outfiles['train-groupId'] = os.path.join(out_dir, 'groupIdFile.txt' )
        outfiles['train-textId'] = os.path.join(out_dir, 'textIdFile.txt' )

        outfiles['train-node'] = os.path.join(out_dir, 'nodeFeaturesTrain.txt' )
        outfiles['test-node'] = os.path.join(out_dir, 'nodeFeaturesTest.txt' )

        outfiles['train-text'] = os.path.join(out_dir, 'textFeaturesTrain.txt' )
        outfiles['test-text'] = os.path.join(out_dir, 'textFeaturesTest.txt' )

        outfiles['train-edge'] = os.path.join(out_dir, 'edgeFeaturesTrain.txt' )
        outfiles['test-edge'] = os.path.join(out_dir, 'edgeFeaturesTest.txt' )

        SandboxAdapter.write_node_features( outfiles['train-node'], self.iilut, self.lt, self.train_it, self.train_iit )
        SandboxAdapter.write_node_features( outfiles['test-node'], self.iilut, self.lt, self.test_it, self.test_iit )
        SandboxAdapter.write_edge_features( outfiles['train-edge'], self.train_et)
        SandboxAdapter.write_edge_features( outfiles['test-edge'], self.test_et)
        SandboxAdapter.write_text_features( outfiles['train-text'], self.train_it, self.train_iit, self.iilut )
        SandboxAdapter.write_text_features( outfiles['test-text'], self.test_it, self.test_iit, self.iilut )
        SandboxAdapter.write_id_file( outfiles['train-groupId'], self.train_it, self.train_iit, self.iilut )
        SandboxAdapter.write_text_id_file( outfiles['train-textId'], self.train_it, self.train_iit, self.iilut )

        for (label, id) in self.lt.label2id.iteritems():
            label_fn = os.path.join(out_dir, 'labels_%02d_%s.txt' % (id,label))
            model_fn = os.path.join(out_dir, 'models_%02d_%s.txt' % (id,label))
            conf_fn = os.path.join(out_dir, '%02d-%s.conf' % (id, label))
            with open( conf_fn, 'w') as f:
                f.write('''
//
// Based on flickr_bmrm/bmrm-2.1/groups-bmrm/config_temp_airplane.conf
//

string Solver.type BMRM

int BMRM.verbosity 2
int BMRM.convergenceLog 0
int BMRM.maxNumOfIter 500

// tolerance for epsilon termination criterion (set negative value to disable this criterion)
double BMRM.epsilonTol 1e-3

// tolerance for gamma termination criterion (set negative value to disable this criterion)
double BMRM.gammaTol -1

// [optional] other possible choices {L2N2_prLOQO, L1N1_CLP}
string BMRM.innerSolverType L2N2_qld

int InnerSolver.verbosity 0
string InnerSolver.gradType DENSE

// [optional] maximum number of projection (to a feasible set) iterations
int L2N2_DaiFletcherPGM.maxProjIter 200

// [optional] maximum numnber of gradient projection iterations
int L2N2_DaiFletcherPGM.maxPGMIter 100000

// [optional] number of iterations an inactive gradient is allowed to remain in
int L2N2_DaiFletcherPGM.gradIdleAge 10

// [optional] maximum gradient set size
int L2N2_DaiFletcherPGM.maxGradSetSize 5000

// [optinal] tolerance
double L2N2_DaiFletcherPGM.tolerance 1e-5

string Loss.lossFunctionType GENERIC


double EpsilonInsensitiveLoss.epsilon 0.1

// verbosity level
int Loss.verbosity 1

int Data.verbosity 1
int Data.biasFeature 0
string Data.format GENERIC

//////////////////////////////////////////////////
// GENERIC parameters                           //
//////////////////////////////////////////////////

bool L2N2_BMRMDualInnerSolver.positivityConstraint true
bool Data.trainingEvidence false

bool Data.baseline false
bool Data.useTagFeatures true
bool Data.useGroupFeatures true
bool Data.useSocialFeatures true
bool Data.useImageFeatures false
bool Data.useNodeFeatures true
double BMRM.lambda 0.001
''')
                f.write('string Data.nodeFeaturesTrain %s\n' % outfiles['train-node'] )
                f.write('string Data.nodeFeaturesTest %s\n' % outfiles['test-node'] )
                f.write('string Data.textFeaturesTrain %s\n' % outfiles['train-text'] )
                f.write('string Data.textFeaturesTest %s\n' % outfiles['test-text'] )
                f.write('string Data.edgeFeaturesTrain %s\n' % outfiles['train-edge'] )
                f.write('string Data.edgeFeaturesTest %s\n' % outfiles['test-edge'] )
                f.write('string Data.imageFeaturesTrain null\n');
                f.write('string Data.imageFeaturesTest null\n');
                f.write('string Data.idFile %s\n' % outfiles['train-groupId'])
                f.write('string Data.textIdFile %s\n' % outfiles['train-textId'])
                f.write('string Data.labelOutput %s\n' % label_fn )
                f.write('int Data.learnLabel %d\n' % id )
                f.write('string Model.modelFile %s\n' % model_fn )

            sys.stderr.write('Info: wrote %s\n' % conf_fn )

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: $0 output-dir\n')
        sys.exit(1)
    out_dir = (sys.argv[1])
    if not os.path.isdir( out_dir ):
        os.mkdir(out_dir)

    s = SandboxAdapter('.')
    s.load()
    s.write( out_dir )
