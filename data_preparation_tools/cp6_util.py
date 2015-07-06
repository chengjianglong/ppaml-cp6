##
## handy methods
##

class CP6Util:

    @staticmethod
    def qstr( s ):
        if not s:
            return 'none'

        s = s.replace( '"',' ' ).replace( '\n', ' ').replace( '\r', ' ' )
        return ( '"%s"' % s ).encode( "UTF-8" )
