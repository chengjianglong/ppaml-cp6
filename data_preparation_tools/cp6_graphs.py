##
## Generate some eye candy
##

import sys
import functools
from igraph import *
from igraph.drawing.text import TextDrawer
from cp6_paths import CP6Paths
from cp6_util import CP6Util
from cp6_image_edge import CP6ImageEdge
import cairo

(PHASE, LABEL) = ('r1train', 'sea')

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
                         (LABEL, tag, len(nodes), len(graph_edges)), halign=TextDrawer.LEFT)
    drawer.draw_at(10,1900,width=1900)
    plot.save()
    sys.stderr.write("Info: wrote %s\n" % output_fn)


p = CP6Paths()
nodes = CP6Util.nodes_with_label(p, PHASE, LABEL)
edges = CP6ImageEdge.edges_in_nodeset( p, PHASE, nodes)

# map node and edge IDs to graph vertex ordinals
node_id_map = dict( [val, idx] for (idx, val) in enumerate(nodes))

make_graph( node_id_map, nodes, edges, shared_groups_only, "sea.group-only.png", "shared groups only")
make_graph( node_id_map, nodes, edges, shared_flags_only, "sea.flags-only.png", "same user/location/contact only")
make_graph( node_id_map, nodes, edges, all_edges, "sea.all-edges.png", "any relationship")
for n in (1,2,5,10,15,20):
    make_graph( node_id_map, nodes, edges, functools.partial(only_N_shared_words, N=n), "sea.%02d-shared-word.png" % n , "Exactly %d shared word(s)" % n)

    
