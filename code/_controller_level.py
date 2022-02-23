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
        self.reset_data()
        self._level_colors = [ utils.hex_to_rgb( c ) for c in O_COLORS ]

        # Load the level data from 'level.txt'
        self.load_level( 'level_main' )

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.__engine, LAYER_BLOCK, self.draw )

    # Initially creates local data; can also be used to reset data
    def reset_data( self ):

        self.__loaded_chunks = [] # Holds a position vector for each currently loaded chunk
        self.__level_meta = {} # Holds additional important info (e.g. player spawn)
        self.__level_surf = None # Test

    # Specifically resets level metadata
    def reset_meta( self, level_surf ):

        # Must loop through file to determine player spawnpoint
        player_spawn = V2()
        for xx in range( level_surf.get_width() ):
            for yy in range( level_surf.get_height() ):
                if ( level_surf.get_at( ( xx, yy ) ) == ( 255, 255, 255, 255 ) ):
                    player_spawn = V2( xx, yy )

        self.__level_meta = {
            'size': level_surf.get_size(),
            'player_spawn': player_spawn.l(),
            'deaths': 0,
            'time': 0,
            'abilities': []
        }

    # Loads the level data into memory
    def load_level( self, level_name ):

        self.reset_data()
        self.__c_block.reset_buffers()
        self.__c_block.reset_data()
        self._level_name = level_name

        try:
            self.__level_surf = pygame.image.load( self.__engine.get_path( f'/data/{ self._level_name }/level.png' ) )
        except FileNotFoundError:
            print( 'Level file "level.png" not found' )

        # Re-create level metadata if necessary
        try:
            level_meta = open( self.__engine.get_path( f'/data/{ self._level_name }/level_meta.json' ) )
            self.__level_meta = json.load( level_meta )
        except ( FileNotFoundError, json.decoder.JSONDecodeError ):
            self.reset_meta( self.__level_surf )

    # Loads necessary chunks into memory based off of view position
    def update( self ):

        # Draw chunks within the proper bound
        # Bound is specified in blocks offset from view center (via RENDER_BOUNDS)
        chunk_pos = self.__engine.view_pos.c().fn( lambda a: floor( a / GRID / C_GRID ) )
        chunk_bound_1 = chunk_pos.c().s( RENDER_BOUNDS )
        chunk_bound_2 = chunk_pos.c().a( RENDER_BOUNDS )

        # Load any chunks within the bound
        # Only loads 1 chunk per frame
        chunk_list = []
        chunks_loaded = 0

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
                
                entity_id = self.get_entity_type( entity_pos )
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

    # Get the metadata of the whole level
    def get_level_meta( self, key ):

        return self.__level_meta[ key ]

    # Set and save metadata
    def set_level_meta( self, key, value, do_save = True ):

        # Data is saved as JSON
        if key in self.__level_meta:
            self.__level_meta[ key ] = value
        if do_save:
            self.save_level_meta()

    # Save all metadata
    def save_level_meta( self ):
        
        meta_file = open( self.__engine.get_path( f'/data/{ self._level_name }/level_meta.json' ), 'w' )
        try:
            meta_file.write( json.dumps( self.__level_meta ) )
        finally:
            meta_file.close()

    # Check whether anything exists at a position
    def is_object( self, pos ):

        return self.__level_surf.get_at( pos.l() )[3] == 255
        # return self.__objects[ pos ] != -1

    # Check whether a block exists at a position
    def is_block( self, pos ):

        try:
            color = self.__level_surf.get_at( pos.l() )
            if color[3] == 0:
                return False
            return utils.obj_id_to_block( self._level_colors.index( color ) ) != None
        except ( IndexError, ValueError ):
            return False

    # Check whether an entity exists at a position
    def is_entity( self, pos ):

        try:
            color = self.__level_surf.get_at( pos.l() )
            if color[3] == 0:
                return False
            return utils.obj_id_to_entity( self._level_colors.index( color ) ) != None
        except ( IndexError, ValueError ):
            return False

    # Get the object id of a position
    def get_object_type( self, pos ):

        return self._level_colors.index( self.__level_surf.get_at( pos.l() ) )

    # Get the block type of a position
    def get_block_type( self, pos ):

        return utils.obj_id_to_block( self._level_colors.index( self.__level_surf.get_at( pos.l() ) ) )

    # Get the entity type of a position
    def get_entity_type( self, pos ):

        return utils.obj_id_to_entity( self._level_colors.index( self.__level_surf.get_at( pos.l() ) ) )

    # Performs an operation on the block the player is hovering over
    def object_debug( self ):

        cursor_pos = self.__engine.get_world_cursor().fn( lambda a: int( a // ( GRID ) ) )
        print( self.is_block( cursor_pos ) )

    # Getters/setters

    @property
    def controller( self ):
        return self._controller