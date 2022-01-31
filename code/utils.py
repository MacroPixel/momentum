from engine.engine import *

# For miscellaneous functions
class utils:

    # Checks for a collision between two rectangles defined by their position and dimensions (using AABB, of course)
    @staticmethod
    def collision_check( pos1, pos2, dim1, dim2 ):

        return ( pos1.x < pos2.x + dim2.x and pos2.x < pos1.x + dim1.x ) and ( pos1.y < pos2.y + dim2.y and pos2.y < pos1.y + dim1.y )

    # Gets the push vector from a collision, assuming the first object is dynamic
    @staticmethod
    def collision_get( pos1, pos2, dim1, dim2 ):

        overlap = V2( ( dim1.x + dim2.x ) * 0.5 - abs( pos1.x - pos2.x ), ( dim1.y + dim2.y ) * 0.5 - abs( pos1.y - pos2.y ) )

        overlap.x *= ( -1 if pos1.x < pos2.x else 1 )
        overlap.y *= ( -1 if pos1.y < pos2.y else 1 )

        return overlap

    # Gets the key of a value in a dictionary
    @staticmethod
    def key_value( dictionary, value ):

        return list( dictionary.keys() )[ list( dictionary.values() ).index( value ) ]

    # Vector / string transformation
    @staticmethod
    def vec_to_str( value ):
        return ':'.join( value.c().fn( lambda a: str( a ) ).l() )

    @staticmethod
    def str_to_vec( value ):
        return V2( value.split( ':' ) ).i()

    # Combines two surfaces together
    # The second surface replaces the first one in the region specified by "rect"
    # Note that it replaces the surface's pixels instead of drawing over it
    @staticmethod
    def stitch_sprites( primary_surf, secondary_surf, rect ):

        secondary_surf = secondary_surf.subsurface( rect ).copy()

        primary_surf.fill( ( 0, 0, 0, 0 ), rect = rect )
        primary_surf.blit( secondary_surf, rect[0:2] )
        return primary_surf