from basic_imports import *
from _controller_block import *
from enemy_list import *
from checkpoint import *
import random

# Contained within/controlled by Controller
# Handles level loading, blocks, and enemies
# More complex block functionality is handled
# by a BlockController contained within the LevelController
class LevelController():

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.__engine = self.controller.engine

        # Handles complex block operations
        self.__c_block = BlockController( self )

        # Basic data
        # Initialized with a function to allow easy resetting
        self.reset_data()

        # Load the level data from 'level.txt'
        self.load_level()

    # Initially creates local data; can also be used to reset data
    def reset_data( self ):

        self.__objects = {} # Maps a position vector to an object ID
        self.__object_meta = {} # Maps a position vector to a dictionary with object metadata
        self.__chunks = {} # Maps a chunk vector to a list of position vectors
        self.__loaded_chunks = [] # Holds a position vector for each currently loaded chunk

    # Loads the level data into memory
    def load_level( self ):

        level_data = open( self.controller.engine.get_path( '/data/level.txt' ) ).read().split( '\n' )

        # Reset any pre-existing level data
        self.reset_data()
        self.__c_block.reset_data()

        # Level data in the level file is grouped into chunks (denoted by "* X:Y")
        # This is done to make chunk loading more performant
        chunk_coords = None

        # Iterate through every line in the file
        for line in level_data:

            # If blank line, do nothing
            if len( line ) == 0:
                pass

            # Otherwise, if * is encountered, switch chunk
            elif line[0] == '*':

                # Try initializing blank chunk
                try:

                    line = line[2:]
                    chunk_coords = V2( line.split( ':' ) ).i()
                    self.__chunks[ chunk_coords ] = []

                except ( ValueError, IndexError ):
                    raise RuntimeError( 'Invalid chunk format' )

            # Otherwise, create a block or enemy under the current chunk
            else:

                # Chunk must be active
                # (You can't specify an object before specifying a chunk)
                if ( chunk_coords is None ):
                    raise RuntimeError( 'No chunk was specified' )

                # Split the line by spaces
                # The first token is the object, and the subsequent tokens
                # represent coordinate pairs relative to the current chunk
                line = line.split( ' ' )
                object_id = utils.o_id( line[0] )
                object_positions = [ V2( line[ i : i + 2 ] ).i() for i in range( 1, len( line ), 2 ) ]

                # Now, loop through coordinates and set the objects
                for rel_coord in object_positions:
                    self.__set_object( utils.chunk_pos_to_block( chunk_coords, rel_coord ), object_id )

        # Create checkpoints
        checkpoint_data = open( self.controller.engine.get_path( '/data/checkpoints.txt' ) ).read().split( '\n' )

        for line in checkpoint_data:

            # If blank line, do nothing
            if len( line ) == 0:
                pass

            # Otherwise, create checkpoint
            else:
                Checkpoint( self.controller.engine, V2( line.split( ' ' ) ).i() )

    # Recreates the level data from a PNG image
    def rewrite_level( self ):

        # Load the PNG into memory
        level_surf = pygame.image.load( self.controller.engine.get_path( '/data/level.png' ) )

        keys = {} # The position of every object in the PNG
        origin = V2( 0, 0 ) # Where the player spawns

        # Loop through all the pixels in the PNG
        for xx in range( level_surf.get_width() ):
            for yy in range( level_surf.get_height() ):

                pos = V2( xx, yy )
                this_color = level_surf.get_at( pos.l() )

                # Create the player if the pixel is white
                if ( this_color == ( 255, 255, 255, 255 ) ):
                    origin = pos

                # Create special objects
                elif ( this_color == O_COLOR_CHECKPOINT ):
                    keys[ pos ] = 'checkpoint'

                # Otherwise, create the appropriate object based on color
                else:
                    for i in range( len( O_STRINGS ) ):
                        if level_surf.get_at( pos.l() ) == O_COLORS[i]:
                            keys[ pos ] = i

        # Store the real position of every object,
        # relative to the origin instead of top-left of image
        chunks = {}

        for pos in keys:

            new_pos = pos.c().s( origin )
            chunk_pos, rel_pos = utils.block_pos_to_chunk( new_pos )

            if chunk_pos not in chunks:
                chunks[ chunk_pos.c() ] = {}

            chunks[ chunk_pos.c() ][ rel_pos ] = keys[ pos ]

        # Actually write to the file
        file = open( self.controller.engine.get_path( '/data/level.txt' ), 'w' )
        file_checkpoint = open( self.controller.engine.get_path( '/data/checkpoints.txt' ), 'w' )
        for chunk in chunks:

            # Write the chunk string
            file.write( f"* { utils.vec_to_str( chunk ) }\n" )

            # Write all the block strings
            for block_pos in chunks[ chunk ]:

                object_id = chunks[ chunk ][ block_pos ]

                # Create checkpoint
                if ( object_id == 'checkpoint' ):

                    output_pos = utils.vec_to_str( utils.chunk_pos_to_block( chunk, block_pos ) ).replace( ':', ' ' )
                    file_checkpoint.write( f'{ output_pos }\n' )

                else:

                    output_pos = utils.vec_to_str( block_pos ).replace( ':', ' ' )
                    file.write( f'{ utils.o_string( object_id ) } { output_pos }\n' )

    # Loads necessary chunks into memory based off of view position
    def update( self ):

        # Draw chunks within the proper bound
        # Bound is specified in blocks offset from view center (via RENDER_BOUNDS)
        bound_1 = self.__engine.view_pos.c().fn( lambda a: round( a / GRID / C_GRID ) ).s( RENDER_BOUNDS )
        bound_2 = self.__engine.view_pos.c().fn( lambda a: round( a / GRID / C_GRID ) ).a( RENDER_BOUNDS )

        # Iterate through every chunk within the bounds
        # All positions are stored in a list so chunk unloading can be performed
        chunk_list = []
        for xx in range( bound_1.x, bound_2.x + 1 ):
            for yy in range( bound_1.y, bound_2.y + 1 ):

                chunk_pos = V2( xx, yy )
                chunk_list.append( chunk_pos.c() )

                # Don't bother if the chunk has no data within it
                if ( chunk_pos not in self.__chunks ):
                    continue

                # Otherwise, load the chunk if it's unloaded
                if ( chunk_pos not in self.__loaded_chunks ):
                    self.load_chunk( chunk_pos )

        # Unload any chunks that aren't within the bounds
        for chunk_pos in self.__loaded_chunks:

            if ( chunk_pos not in chunk_list ):
                self.unload_chunk( chunk_pos )

    # Loading a chunk involves spawning enemies
    # and creating a surface buffer for fast drawing
    def load_chunk( self, chunk_pos ):

        self.__loaded_chunks.append( chunk_pos.c() )

        # Spawn any enemies within the chunk
        for pos in self.__chunks[ chunk_pos.c() ]:

            # Creates the enemy using an exec() of a string representation of a class
            # There's probably a better way of doing this, and I'm all ears
            enemy_pos = pos
            if ( self.is_enemy( enemy_pos ) ):
                
                enemy_id = utils.obj_id_to_enemy( self.get_object_type( enemy_pos ) )
                engine_ref = self.__engine # Can't access class variables from exec statement
                exec( f"{ ENEMY_CLASSES[ enemy_id ] }( engine_ref, enemy_pos )" )

        # Create the surface buffer
        self.__c_block.create_buffer( chunk_pos )

    # Undoes chunk loading
    def unload_chunk( self, chunk_pos ):

        self.__loaded_chunks.remove( chunk_pos )

        # Delete the surface buffer
        self.__c_block.delete_buffer( chunk_pos )
            
    # Only responsible for drawing blocks
    # Since enemies are their own objects, they're capable of drawing themselves
    # This is a little convoluted, but it's necessary for performance
    def draw( self ):

        self.__c_block.draw()

    # Set block/enemy at target position
    def __set_object( self, pos, object_id ):

        # Initialize the object data
        self.__objects[ pos ] = object_id
        self.__object_meta[ pos ] = {}

        block_id = utils.obj_id_to_block( object_id )
        enemy_id = utils.obj_id_to_enemy( object_id )

        # Do any necessary block setup
        if ( block_id is not None ):
            if ( B_DRAW_MODES[ block_id ] in [ BDM_3VAR_OVERLAY, BDM_3VAR_REPLACE ] ):
                self.__object_meta[ pos ][ 'var' ] = random.randint( 0, 2 )
            else:
                self.__object_meta[ pos ][ 'var' ] = 0

        # Do any necessary enemy setup
        elif ( enemy_id ):
            pass

        # Make sure this position is stored within the chunk
        chunk_pos, rel_pos = utils.block_pos_to_chunk( pos )
        if ( rel_pos not in self.__chunks[ chunk_pos.c() ] ):
            self.__chunks[ chunk_pos.c() ].append( rel_pos )

    # Checks if a chunk exists at a chunk position
    def is_chunk( self, chunk_pos ):

        return chunk_pos in self.__chunks

    # Check whether anything exists at a position
    def is_object( self, pos ):

        return pos in self.__objects

    # Check whether a block exists at a position
    def is_block( self, pos ):

        try:
            return utils.obj_id_to_block( self.__objects[ pos ] ) != None
        except KeyError:
            return False

    # Check whether an enemy exists at a position
    def is_enemy( self, pos ):

        try:
            return utils.obj_id_to_enemy( self.__objects[ pos ] ) != None
        except KeyError:
            return False

    # Get the object id of a position
    # !!! WILL throw error if there isn't an object there
    def get_object_type( self, pos ):

        return self.__objects[ pos ]

    # Get the object metadata of a position
    # !!! WILL throw error if there isn't an object there
    def get_object_meta( self, pos ):

        return self.__object_meta[ pos ]

    # Performs an operation on the block the player is hovering over
    def object_debug( self ):

        cursor_pos = self.controller.engine.get_world_cursor()
        print( 'Cursor in chunk', cursor_pos.fn( lambda a: int( a // ( GRID * C_GRID ) ) ) )

    # Getters/setters

    @property
    def controller( self ):
        return self._controller