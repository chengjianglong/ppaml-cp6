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
## Generate some eye candy
##

import sys
import functools

import cairo
from igraph import *
from igraph.drawing.text import TextDrawer

from cp6.utilities.paths import Paths
from cp6.utilities.util import Util
from cp6.tables.cp6_image_edge import CP6ImageEdge

(PHASE, LABEL) = ('r1train', 'car')

def shared_groups_only( e ):
    return (len(e.shared_groups) > 0) and \
        (len(e.shared_words) == 0) and \
        (e.same_user_flag != '1') and \
        (e.same_location_flag != '1') and \
        (e.shared_contact_flag != '1')

def shared_flags_only( e ):
    return (len(e.shared_groups) == 0) and \
        (len(e.shared_words) == 0) and \
        (   (e.same_user_flag == '1') or \
            (e.same_location_flag == '1') or \
            (e.shared_contact_flag == '1'))

def all_edges(e):
    return True

def only_N_shared_words( e, N ):
    return (len(e.shared_groups) == 0) and \
        (len(e.shared_words) == N ) and \
        (e.same_user_flag != '1') and \
        (e.same_location_flag != '1') and \
        (e.shared_contact_flag != '1')

def make_graph( node_id_map, nodes, edges, edges_predicate, output_fn, tag ):
    g = Graph()
    g.add_vertices( len(nodes))
    graph_edges = list( [node_id_map[e.image_A_id], node_id_map[e.image_B_id]] \
                         for e in edges if edges_predicate(e))
    g.add_edges( graph_edges)
    layout = g.layout_circle()
    # adding text to plot courtesy http://stackoverflow.com/questions/18250684/add-title-and-legend-to-igraph-plots
    plot = Plot(output_fn, bbox=[2000,2000])
    plot.add( g, layout=layout, bbox=[50,50,1950,1950])
    ctx = cairo.Context( plot.surface )
    ctx.set_font_size(36)
    drawer = TextDrawer( ctx, "Label: '%s'\n%s\n%d nodes, %d edges" % \
                         (LABEL, tag, len(nodes), len(graph_edges)), halign=TextDrawer.RIGHT)
    drawer.draw_at(10,1900,width=1900)
    plot.save()
    sys.stderr.write("Info: wrote %s\n" % output_fn)


p = Paths()
nodes = Util.nodes_with_label(p, PHASE, LABEL)
edges = CP6ImageEdge.edges_in_nodeset( p, PHASE, nodes)

# map node and edge IDs to graph vertex ordinals
node_id_map = dict( [val, idx] for (idx, val) in enumerate(nodes))

make_graph( node_id_map, nodes, edges, shared_groups_only, "%s.group-only.png" % LABEL, "shared groups only")
make_graph( node_id_map, nodes, edges, shared_flags_only, "%s.flags-only.png" % LABEL, "same user/location/contact only")
make_graph( node_id_map, nodes, edges, all_edges, "%s.all-edges.png" % LABEL, "any relationship")
for n in (1,2,5,10,15,20):
    make_graph( node_id_map, nodes, edges, functools.partial(only_N_shared_words, N=n), "%s.%02d-shared-word.png" % (LABEL, n) , "Exactly %d shared word(s)" % n)
