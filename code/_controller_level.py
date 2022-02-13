from basic_imports import *
from _controller_block import *
from entity_list import *
from drawer import *

import random
import json

# Contained within/controlled by Controller
# Handles level loading, blocks, and enemies
# More complex block functionality is handled
# by a BlockController contained within the LevelController
class LevelController:

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.__engine = self.controller.engine

        # Handles complex block operations
        self.__c_block = BlockController( self )

        # Basic data
        # Initialized with a function to allow easy resetting
        self.reset_data( ( 1, 1 ) )

        # Load the level data from 'level.txt'
        self.load_level( 'level_main' )

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.__engine, LAYER_BLOCK, self.draw )

    # Initially creates local data; can also be used to reset data
    def reset_data( self, level_size ):

        self.__objects = {} # Maps a position vector to an object ID
        self.__chunks = {} # Maps a chunk vector to a list of position vectors
        self.__loaded_chunks = [] # Holds a position vector for each currently loaded chunk
        self.__level_meta = {} # Holds additional important info (e.g. player spawn)

    # Loads the level data into memory
    def load_level( self, level_name ):

        # Reset any pre-existing level data
        self._level_name = level_name
        level_data = open( self.__engine.get_path( f'/data/{ self._level_name }/level.txt' ) ).read().split( '\n' )
        level_meta = open( self.__engine.get_path( f'/data/{ self._level_name }/level_meta.json' ) )
        level_meta = json.load( level_meta )

        self.reset_data( level_meta[ 'size' ] )
        self.__c_block.reset_buffers()
        self.__c_block.reset_data()

        # Initially parse level metadata
        self.__level_meta = level_meta

        # Iterate through every line in the file
        for line in level_data:

            # If blank line, do nothing
            if len( line ) == 0:
                pass

            # Otherwise, create a block/entity at the listed positions
            else:

                # Split the line by spaces
                # The first token is the object ID, and the subsequent tokens
                # represent coordinate pairs at which the objects should be created
                line = line.split( ' ' )
                object_id = utils.o_id( line[0] )
                object_positions = [ V2( line[ i : i + 2 ] ).i() for i in range( 1, len( line ), 2 ) ]

                # Now, loop through coordinates and set the objects
                for obj_pos in object_positions:
                    self._set_object( obj_pos, object_id )
        
    # Recreates the level data from a PNG image
    def rewrite_level( self ):

        # Load the PNG into memory
        level_surf = pygame.image.load( self.__engine.get_path( f'/data/{ self._level_name }/level.png' ) )

        objects = {} # Lists an object ID and all the positions associated with it
        player_spawn = V2( 0, 0 ) # Player spawnpoint can be changed

        # Find the positions of each object relative to top-left
        # using the defined color values
        for xx in range( level_surf.get_width() ):
            for yy in range( level_surf.get_height() ):
                
                # Store color of pixel
                pos = V2( xx, yy )
                this_color = level_surf.get_at( pos.l() )

                # Skip if transparent
                if ( this_color[3] == 0 ):
                    continue

                # Change the player spawn if the pixel is white
                if ( this_color == ( 255, 255, 255, 255 ) ):
                    player_spawn = pos
                    continue

                # Otherwise, store the position in the appropriate object
                for object_id in range( len( O_STRINGS ) ):
                    if ( level_surf.get_at( pos.l() ) == utils.hex_to_rgb( O_COLORS[ object_id ] ) ):

                        if ( object_id not in objects ):
                            objects[ object_id ] = []
                        objects[ object_id ].append( pos )

        # Actually write to the file
        file = open( self.__engine.get_path( f'/data/{ self._level_name }/level.txt' ), 'w' )
        for object_id in objects:

            # Create a list of all the positions at which this object should be created
            # Positions are relative to the player spawn, hence the .s( player_spawn )
            object_positions = [ utils.vec_to_str( pos ).replace( ':', ' ' ) for pos in objects[ object_id ] ]
            file.write( f"{ utils.o_string( object_id ) } { ' '.join( object_positions ) }\n" )

        # Write data to metadata file
        meta_file = open( self.__engine.get_path( f'/data/{ self._level_name }/level_meta.json' ), 'w' )
        meta_dict = {
            'size': level_surf.get_size(),
            'player_spawn': player_spawn.l()
        }
        meta_file.write( json.dumps( meta_dict ) )

    # Loads necessary chunks into memory based off of view position
    def update( self ):

        # Draw chunks within the proper bound
        # Bound is specified in blocks offset from view center (via RENDER_BOUNDS)
        chunk_pos = self.__engine.view_pos.c().fn( lambda a: floor( a / GRID / C_GRID ) )
        chunk_bound_1 = chunk_pos.c().s( RENDER_BOUNDS )
        chunk_bound_2 = chunk_pos.c().a( RENDER_BOUNDS )

        # Load any chunks within the bound
        chunk_list = []

        for xx in range( chunk_bound_1.x, chunk_bound_2.x + 1 ):
            for yy in range( chunk_bound_1.y, chunk_bound_2.y + 1 ):
                chunk_pos = V2( xx, yy )
                chunk_list.append( chunk_pos.c() )
                self.load_chunk( chunk_pos )

        # Unload any chunks not within the bounds
        for chunk_pos in self.__loaded_chunks:
            if ( chunk_pos not in chunk_list ):
                self.unload_chunk( chunk_pos )

    # Loading a chunk involves spawning enemies
    # and creating a surface buffer for fast drawing
    def load_chunk( self, chunk_pos ):

        # Don't bother if chunk is loaded
        if chunk_pos in self.__loaded_chunks:
            return
        self.__loaded_chunks.append( chunk_pos.c() )

        # Spawn any entities within the chunk
        obj_positions = []
        for xx in range( C_GRID ):
            for yy in range( C_GRID ):
                obj_positions.append( V2( xx, yy ) )

        for pos in obj_positions:

            # Creates the entity using an exec() of a string representation of a class
            # There's probably a better way of doing this, and I'm all ears
            entity_pos = utils.chunk_pos_to_block( chunk_pos, pos )
            if ( self.is_entity( entity_pos ) ):
                
                entity_id = utils.obj_id_to_entity( self.get_object_type( entity_pos ) )
                engine_ref = self.__engine # Can't access class variables from exec statement
                exec( f"{ ENTITY_CLASSES[ entity_id ] }( engine_ref, entity_pos )" )

        # Create the surface buffer
        self.__c_block.create_buffer( chunk_pos )

    # Undoes chunk loading
    def unload_chunk( self, chunk_pos ):

        # Don't bother if chunk is unloaded
        if chunk_pos not in self.__loaded_chunks:
            return
        self.__loaded_chunks.remove( chunk_pos )

        # Delete the surface buffer
        self.__c_block.delete_buffer( chunk_pos )

        # Delete any objects within the chunk
        for obj in [ o for o in self.__engine.get_tagged_instances( 'entity' ) if o.object_id != 'player' ]:

            obj_chunk_pos = obj.pos.c().fn( lambda a: floor( a / C_GRID ) )
            if obj_chunk_pos == chunk_pos:
                obj.delete()
            
    # Only responsible for drawing blocks
    # Since enemies are their own objects, they're capable of drawing themselves
    # This is a little convoluted, but it's necessary for performance
    def draw( self ):

        self.__c_block.draw()

    # Set block/entity at target position
    def _set_object( self, pos, object_id ):

        # Initialize the object data
        self.__objects[ pos ] = object_id

        block_id = utils.obj_id_to_block( object_id )
        entity_id = utils.obj_id_to_entity( object_id )

        # Do any necessary block setup
        if ( block_id is not None ):
            pass

        # Do any necessary entity setup
        elif ( entity_id is not None ):
            pass

        # Make sure the parent chunk exists, then store
        # the position and object ID within the parent chunk
        chunk_pos, rel_pos = utils.block_pos_to_chunk( pos )
        if chunk_pos not in self.__chunks:
            self.__chunks[ chunk_pos.c() ] = []
        if ( rel_pos not in self.__chunks[ chunk_pos ] ):
            self.__chunks[ chunk_pos ].append( rel_pos )

    # Get the metadata of the whole level
    def get_level_meta( self, key ):

        return self.__level_meta[ key ]

    # Check whether anything exists at a position
    def is_object( self, pos ):

        return self.__objects[ pos ] != -1

    # Check whether a block exists at a position
    def is_block( self, pos ):

        try:
            return utils.obj_id_to_block( self.__objects[ pos ] ) != None
        except KeyError:
            return False

    # Check whether an entity exists at a position
    def is_entity( self, pos ):

        try:
            return utils.obj_id_to_entity( self.__objects[ pos ] ) != None
        except KeyError:
            return False

    # Get the object id of a position
    def get_object_type( self, pos ):

        return self.__objects[ pos ]

    # Performs an operation on the block the player is hovering over
    def object_debug( self ):

        cursor_pos = self.__engine.get_world_cursor()
        print( 'Cursor in chunk', cursor_pos.fn( lambda a: int( a // ( GRID * C_GRID ) ) ) )

    # Getters/setters

    @property
    def controller( self ):
        return self._controller