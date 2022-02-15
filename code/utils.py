from engine.engine import *
from constants import *
from math import floor, ceil, atan, pi

# For miscellaneous functions
class utils:

    @staticmethod
    def sign( x ):

        if x == 0:
            return 0
        return -1 if x < 0 else 1

    # Linear interpolation
    # d argument can act as delta time
    @staticmethod
    def lerp( a, b, x, d = 1 ):

        return ( b + ( a - b ) * ( ( 1 - x ) ** d ) )

    # Find the distance between two vectors
    @staticmethod
    def dist( pos_a, pos_b ):

        return abs( ( pos_b.x - pos_a.x ) ** 2 + ( pos_b.y - pos_a.y ) ** 2 ) ** 0.5

    # Checks for a collision between two rectangles defined by their position and dimensions (using AABB, of course)
    @staticmethod
    def collision_check( pos_a, pos_b, dim_a, dim_b, offset_a = V2(), offset_b = V2() ):

        pos_a.a( offset_a )
        pos_b.a( offset_b )

        return ( pos_a.x < pos_b.x + dim_b.x and pos_b.x < pos_a.x + dim_a.x ) and ( pos_a.y < pos_b.y + dim_b.y and pos_b.y < pos_a.y + dim_a.y )

    # Gets the push vector from a collision, assuming the first object is dynamic
    @staticmethod
    def collision_get( pos_a, pos_b, dim_a, dim_b, offset_a = V2(), offset_b = V2() ):

        pos_a.a( offset_a )
        pos_b.a( offset_b )

        overlap = V2( ( dim_a.x + dim_b.x ) * 0.5 - abs( pos_a.x - pos_b.x ), ( dim_a.y + dim_b.y ) * 0.5 - abs( pos_a.y - pos_b.y ) )

        overlap.x *= ( -1 if pos_a.x < pos_b.x else 1 )
        overlap.y *= ( -1 if pos_a.y < pos_b.y else 1 )

        return overlap

    # Returns a RGB or RGBA tuple from a hex string
    @staticmethod
    def hex_to_rgb( str, alpha = True ):

        if alpha:
            return ( int( str[:2], 16 ), int( str[2:4], 16 ), int( str[4:6], 16 ), 255 )
        return ( int( str[:2], 16 ), int( str[2:4], 16 ), int( str[4:6], 16 ) )

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
        return ENTITY_STRINGS.index( string )

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

        if ( 0 <= obj_id < len( B_STRINGS ) ):
            return obj_id
        else:
            return None

    # Checks and converts a object ID to a entity ID
    def obj_id_to_entity( entity_id ):

        if ( len( B_STRINGS ) <= entity_id < len( O_STRINGS ) ):
            return entity_id - len( B_STRINGS )
        else:
            return None

    # Extracts information from a hitbox list
    def get_hitbox_width( hitbox ):

        return V2( hitbox[:2] )

    def get_hitbox_offset( hitbox ):

        return V2( hitbox[2:4] )