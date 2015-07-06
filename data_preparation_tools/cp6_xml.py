import sys
import codecs
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import xml.dom.minidom

class CP6XML:
    def __init__( self, fn ):
        self.xml = ET.parse( fn )
        self.mir_nodes = dict()
        root = self.xml.getroot()
        for photo in root.iter( 'photo' ):
            id = photo.get( 'ppaml_src_id' )
            if id == 'none':
                continue
            self.mir_nodes[ int(id) ] = photo
        sys.stderr.write( 'Info: found %d MIR nodes in XML\n' % len(self.mir_nodes) )

if __name__ == '__main__':
    x = CP6XML( sys.argv[1] )
