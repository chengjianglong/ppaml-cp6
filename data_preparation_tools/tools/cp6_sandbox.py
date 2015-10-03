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

#
# Take a list of image IDs, copy to sandbox directory
#

import sys
import os
import glob
import shutil

from cp6.tables.edge_table import EdgeTable
from cp6.tables.image_table import ImageTable

#
# Given a fully populated set of files, we take a set of IDs:
# {A|B|C} id
# A ids go into training. B ids go into testing. C ids are the eval_in.
#
# Ids may be duplicated between A/B/C.
#
# Each of A, B, and C require a closed set of edges.
#
# etc/
#   label_table
#   image_indicator_lookup_table
#   caffe_descriptor_table
#
# run_in/
#   input/
#     training/  (all over just A ids )
#        image_table [training mode ]
#        image_feature_table
#        image_detector_table
#        image_indicator_table
#        image_csift_table
#        edge_table
#     testing/  (over all just B ids )
#        image_table [testing mode ]
#        image_feature_table
#        image_detector_table
#        image_indicator_table
#        image_csift_table
#        edge_table
#
#  eval_in/ (over all just C ids)
#     image_table [testing mode ]
#     image_feature_table
#     image_detector_table
#     image_indicator_table
#     image_csift_table
#     edge_table
#



class SandboxPaths:
    def __init__( self, src_dir, target_dir ):
        if os.path.exists( target_dir ):
            raise AssertionError( '%s exists; please remove and re-run' % target_dir )
        self.dirs = dict()
        self.dirs[ 'root' ] = target_dir
        self.dirs[ 'etc' ] = os.path.join( target_dir, 'etc' )
        self.dirs[ 'run_in' ] = os.path.join( target_dir, 'run_in' )
        self.dirs[ 'input' ] = os.path.join( target_dir, 'run_in' )
        self.dirs[ 'training' ] = os.path.join( self.dirs[ 'input' ], 'training' )
        self.dirs[ 'testing' ] = os.path.join( self.dirs[ 'input' ], 'testing' )
        self.dirs[ 'test' ] = os.path.join( self.dirs[ 'run_in' ], 'test' )
        self.dirs[ 'eval_in' ] = os.path.join( target_dir, 'eval_in' )

        # order matters
        for d in ['root', 'etc', 'run_in', 'training', 'testing', 'test', 'eval_in' ]:
            os.mkdir( self.dirs[d] )

        self.src_dir = src_dir


    def populate_etc( self ):
        # copy over the files which don't change
        for i in ['caffe_dictionary.txt', 'image_indicator_lookup_table.txt', 'label_table.txt' ]:
            src_fn = os.path.join( self.src_dir,'fixed', i )
            if not os.path.isfile( src_fn ):
                raise AssertionError( 'No file %s' % src_fn )
            shutil.copy( src_fn, os.path.join( self.dirs['etc'], i ))
            sys.stderr.write('Info: copied %s\n' % i)

    def downsample_edge_file( self, dst_dir_tag, ids ):
        e_sampled = self.edge_table.copy_closed_over_ids( ids )
        e_sampled.write_to_file( os.path.join( self.dirs[ dst_dir_tag ], 'image_edge_table.txt' ))

    def downsample_image_file( self, dst_dir_tag, ids, testing_mode_flag ):
        i_sampled = self.image_table.copy_selected_ids( ids, testing_mode_flag )
        i_sampled.write_to_file( os.path.join( self.dirs[ dst_dir_tag ], 'image_table.txt' ))

    def downsample_id_files( self, dst_dir_tag, ids ):
        gsrc =  os.path.join( self.src_dir, 'id-based', '*.txt')
        g = glob.glob( gsrc )
        sys.stderr.write( 'Info: found %d files in %s\n' % (len(g), gsrc))
        for src in g:
            dst = os.path.join( self.dirs[ dst_dir_tag ], os.path.basename( src ))
            c = 0
            with open( src ) as f_in:
                with open (dst, 'w') as f_out:
                    while 1:
                        raw_line = f_in.readline()
                        if not raw_line:
                            break
                        d = raw_line.split()
                        id = int(d[0])
                        if id in ids:
                            f_out.write( raw_line )
                            c += 1
            sys.stderr.write('Info: wrote %d lines to %s\n' % (c, dst ))

    def load_id_files( self, id_fn ):
        self.id_tables = dict()
        self.all_ids = dict()
        with open( id_fn ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                fields = raw_line.split()
                (code, id) = (fields[0], int(fields[1]))
                if not code in self.id_tables:
                    self.id_tables[ code ] = list()
                self.id_tables[ code ].append( id )
                self.all_ids[ id ] = True

    def cache_edge_table( self ):
        edge_src_fn = os.path.join( self.src_dir, 'edge', 'image_edge_table.txt' )
        sys.stderr.write( 'Info: loading edge table %s, filtering to %d edges\n' % (edge_src_fn, len(self.all_ids)) )
        self.edge_table = EdgeTable.read_from_file( edge_src_fn, self.all_ids )
        sys.stderr.write( 'Info: loaded\n')

    def cache_image_table( self ):
        img_src_fn = os.path.join( self.src_dir, 'image', 'image_table.txt' )
        sys.stderr.write( 'Info: loading image table %s, filtering to %d images\n' % (img_src_fn, len(self.all_ids)) )
        self.image_table = ImageTable.read_from_file( img_src_fn, self.all_ids )
        sys.stderr.write( 'Info: loaded\n')

#
#
#

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write( 'Usage: $0 src-dir dst-dir id-file\n' )
        sys.exit(0)
    p = SandboxPaths( sys.argv[1], sys.argv[2] )
    p.load_id_files( sys.argv[3] )
    p.cache_edge_table()
    p.cache_image_table()

    p.populate_etc()

    # run_in/training
    p.downsample_edge_file( 'training', p.id_tables[ 'A' ])
    p.downsample_image_file( 'training', p.id_tables[ 'A' ], False )
    p.downsample_id_files( 'training', p.id_tables[ 'A' ])

    # run_in/testing
    p.downsample_edge_file( 'testing', p.id_tables[ 'B' ])
    p.downsample_image_file( 'testing', p.id_tables[ 'B' ], True )
    p.downsample_id_files( 'testing', p.id_tables[ 'B' ])

    # test
    p.downsample_edge_file( 'test', p.id_tables[ 'C' ])
    p.downsample_image_file( 'test', p.id_tables[ 'C' ], True )
    p.downsample_id_files( 'test', p.id_tables[ 'C' ])


