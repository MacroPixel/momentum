from engine.engine import *
from constants import *
from math import floor, ceil

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

    # Takes the position, velocity, engine, and hitbox of an object
    # And adds to the position with respect to collisions
    @staticmethod
    def move_solid( pos, vel, hitbox, engine, iterations = 5, x_push_func = None, y_push_func = None ):

        # The push functions aren't run until after the iteration is done
        # This prevents them from being executed more than once
        # These variables keep track of whether a push has occured along an axis
        # and which block it was
        x_push_block = y_push_block = None

        for i in range( iterations ):

            pos.x += vel.x * engine.delta_time / iterations
            temp_block = utils.__push_out( pos, vel, hitbox, engine, True, x_push_func )
            if ( temp_block != None ):
                x_push_block = temp_block

            pos.y += vel.y * engine.delta_time / iterations
            temp_block = utils.__push_out( pos, vel, hitbox, engine, False, y_push_func )
            if ( temp_block != None ):
                y_push_block = temp_block

        # Perform the aforementioned push functions
        # Defaults to canceling velocity if nothing else is mentioned
        for xy in 'xy': # Doing it this way reduces boilerplate code

            if eval( f'{xy}_push_block' ):

                # Execute the custom function
                if eval( f'{xy}_push_func' ):
                    exec( f'{xy}_push_func()' )
                
                # Cancel the velocity if it's a normal block
                block_type = B_STRINGS[ eval( f'{xy}_push_block' ) ]
                if ( block_type not in B_BOUNCE ):
                    exec( f'vel.{xy} = 0' )
                elif ( block_type in B_BOUNCE ):
                    exec( f'vel.{xy} *= -BOUNCE_FACTOR' )

    # Push the player out of any adjacent blocks
    # Returns whether a push-put occured
    @staticmethod
    def __push_out( pos, vel, hitbox, engine, is_x_axis, push_func ):

        controller = engine.get_instance( 'controller' )
        adjacent_blocks = utils.__get_adjacent_blocks( pos, hitbox )

        # For every grid space the position is inside of
        for block_pos in adjacent_blocks:

            # Only continue if a block occupies this grid space
            if ( not controller.is_block( block_pos ) ):
                continue

            # Push out based on their position within the block
            # The is_x_axis argument determines the axis it's pushed along
            if ( is_x_axis ):
                direction = -1 if pos.x < block_pos.x else 1
                pos.x = block_pos.x + direction * ( 1 + hitbox.x ) / 2
                return controller.get_block_type( block_pos )
            else:
                direction = -1 if pos.y < block_pos.y else 1
                pos.y = block_pos.y + direction * ( 1 + hitbox.y ) / 2
                return controller.get_block_type( block_pos )
        return None

    # Returns a list of the vectors of any blocks the position is inside of
    @staticmethod
    def __get_adjacent_blocks( pos, hitbox ):

        output = []

        bound_1 = pos.c().a( hitbox.c().m( -1 ).a( 1 ).d( 2 ) ).a( COLLISION_EPSILON )
        bound_2 = pos.c().a( hitbox.c().a( 1 ).d( 2 ) ).s( COLLISION_EPSILON )

        for xx in range( int( floor( bound_1.x ) ), int( ceil( bound_2.x ) ) ):
            for yy in range( int( floor( bound_1.y ) ), int( ceil( bound_2.y ) ) ):    
                output.append( V2( xx, yy ) )
        return output