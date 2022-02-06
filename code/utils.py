from engine.engine import *
from constants import *
from math import floor, ceil

# For miscellaneous functions
class utils:

    # Linear interpolation
    # d argument can act as delta time
    @staticmethod
    def lerp( a, b, x, d = 1 ):

        return ( b + ( a - b ) * ( ( 1 - x ) ** d ) )

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

    # Converts chunk coords to object coords
    # Requires the chunk coords and the relative object coords
    @staticmethod
    def chunk_pos_to_block( chunk_pos, relative_pos ):

        return chunk_pos.c().m( C_GRID ).a( relative_pos )

    # Converts object coords to chunk coords
    # Returns the chunk coords and the relative object coords
    @staticmethod
    def block_pos_to_chunk( obj_pos ):

        chunk_pos = obj_pos.c().fn( lambda a: a // C_GRID )
        relative_pos = obj_pos.c().fn( lambda a: a % C_GRID )
        return ( chunk_pos, relative_pos )

    # Get an ID given a string
    @staticmethod
    def o_id( string ): # Object
        return O_STRINGS.index( string )
    @staticmethod
    def b_id( string ): # Block
        return B_STRINGS.index( string )
    @staticmethod
    def e_id( string ): # Enemy
        return ENEMY_STRINGS.index( string )

    # Get a string given an ID
    @staticmethod
    def o_string( o_id ):
        return O_STRINGS[ o_id ]
    @staticmethod
    def b_string( b_id ):
        return B_STRINGS[ b_id ]
    @staticmethod
    def e_string( e_id ):
        return E_STRINGS[ e_id ]

    # Checks and converts a object ID to a block ID
    def obj_id_to_block( obj_id ):

        if obj_id < len( B_STRINGS ):
            return obj_id
        else:
            return None

    # Checks and converts a object ID to a enemy ID
    def obj_id_to_enemy( enemy_id ):

        if ( len( B_STRINGS ) <= enemy_id < len( O_STRINGS ) ):
            return enemy_id - len( B_STRINGS )
        else:
            return None