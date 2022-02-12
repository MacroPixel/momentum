from basic_imports import *
from _controller_block import *
from entity_list import *
from drawer import *
import random

# Contained within/controlled by Controller
# Handles level loading, blocks, and enemies
# More complex block functionality is handled
# by a BlockController contained within the LevelController
class LevelController:

    RELOAD_INTERVAL = 0.15

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
        self.load_level( 'level_main' )

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.__engine, LAYER_BLOCK, self.draw )

    # Initially creates local data; can also be used to reset data
    def reset_data( self ):

        self.__objects = {} # Maps a position vector to an object ID
        self.__object_meta = {} # Maps a position vector to a dictionary with object metadata
        self.__chunks = {} # Maps a chunk vector to a list of position vectors
        self.__loaded_chunks = [] # Holds a position vector for each currently loaded chunk
        self.__loaded_regions = [] # Holds a vector representing all chunks in memory
        self.__reload_timer = self.RELOAD_INTERVAL # Only reloads chunks every RELOAD_INTERVAL seconds

    # Loads the level data into memory
    def load_level( self, name = 'level_main' ):

        self._level_name = name
        self.reset_data()
        
    # Recreates the level data from a PNG image
    def rewrite_level( self ):

        # Load the PNG into memory
        level_surf = pygame.image.load( self.__engine.get_path( f'/data/{ self._level_name }/level.png' ) )

        # Regions are a group of chunks stored in their own file
        # They prevent having to use all the level data at once
        # Unlike chunks, regions must be calculated during this process
        # instead of being calculated when the file is loaded
        # 'regions' maps a region vector to a dictionary that maps
        # an object to all its positions
        objects = {}
        regions = {}

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
                # Positions are stored in 'objects' until the player's spawnpoint is taken
                # into account; then, they're moved over to 'regions'
                for object_id in range( len( O_STRINGS ) ):
                    if ( level_surf.get_at( pos.l() ) == utils.hex_to_rgb( O_COLORS[ object_id ] ) ):
                        if ( object_id not in objects ):
                            objects[ object_id ] = []
                        objects[ object_id ].append( pos )

        # Shift the object positions relative to the player spawnpoint
        # Now, the objects can be safely grouped into regions
        for object_id in objects:

            # Shift every position
            object_positions = [ pos.c().s( player_spawn ) for pos in objects[ object_id ] ]

            # For each position, find its region vector
            # Then, add it to the region:object:pos dictoinary, creating new keys if necessary
            # Coordinates are NOT stored relative to the current region
            for pos in object_positions:

                region = pos.c().fn( lambda a: floor( a / C_GRID / R_GRID ) )
                if ( region not in regions ):
                    regions[ region ] = {}
                if ( object_id not in regions[ region ] ):
                    regions[ region ][ object_id ] = []
                regions[ region ][ object_id ].append( pos.c() )

        # For every region, create a file, storing the filename in a central 'regions.txt' file
        file_root = open( self.__engine.get_path( f'/data/{ self._level_name }/regions.txt' ), 'w' )
        for region in regions:

            filename = f'rg_{ region.x }_{ region.y }.txt'
            file_root.write( filename + '\n' )
            file = open( self.__engine.get_path( f'/data/{ self._level_name }/{ filename }' ), 'w' )
            for object_id in regions[ region ]:
                object_positions = [ f'{ pos.x } { pos.y }' for pos in regions[ region ][ object_id ] ]
                file.write( f"{ utils.o_string( object_id ) } { ' '.join( object_positions ) }\n" )

    # Loads necessary chunks into memory based off of view position
    def update( self ):

        # Only do this every RELOAD_INTERVAL seconds
        self.__reload_timer += self.__engine.delta_time
        if ( self.__reload_timer > self.RELOAD_INTERVAL ):

            self.__reload_timer = divmod( self.__reload_timer, 0.4 )[1]

            # Draw chunks within the proper bound
            # Bound is specified in blocks offset from view center (via RENDER_BOUNDS)
            bound_1 = self.__engine.view_pos.c().fn( lambda a: round( a / GRID ) ).s( RENDER_BOUNDS )
            bound_2 = self.__engine.view_pos.c().fn( lambda a: round( a / GRID ) ).a( RENDER_BOUNDS )
            chunk_bound_1 = bound_1.c().fn( lambda a: floor( a / C_GRID ) )
            chunk_bound_2 = bound_2.c().fn( lambda a: floor( a / C_GRID ) )
            region_bound_1 = chunk_bound_1.c().s( 1 ).fn( lambda a: floor( a / R_GRID ) )
            region_bound_2 = chunk_bound_2.c().a( 1 ).fn( lambda a: floor( a / R_GRID ) )

            # Load any chunks/regions within the bound
            region_list = []
            chunk_list = []

            for xx in range( region_bound_1.x, region_bound_2.x + 1 ):
                for yy in range( region_bound_1.y, region_bound_2.y + 1 ):
                    region_pos = V2( xx, yy )
                    region_list.append( region_pos.c() )
                    self._load_region( region_pos )

            for xx in range( chunk_bound_1.x, chunk_bound_2.x + 1 ):
                for yy in range( chunk_bound_1.y, chunk_bound_2.y + 1 ):
                    chunk_pos = V2( xx, yy )
                    chunk_list.append( chunk_pos.c() )
                    self.load_chunk( chunk_pos )

            # Unload any chunks/regions not within the bounds
            for chunk_pos in self.__loaded_chunks:
                if ( chunk_pos not in chunk_list ):
                    self.unload_chunk( chunk_pos )
            for region_pos in self.__loaded_regions:
                if ( region_pos not in region_list ):
                    print( region_pos )
                    self._unload_region( region_pos )

    # Loading a chunk involves spawning enemies
    # and creating a surface buffer for fast drawing
    def load_chunk( self, chunk_pos ):

        # Don't bother if chunk is loaded
        if chunk_pos in self.__loaded_chunks:
            return

        # Return early if this chunk is empty
        if chunk_pos not in self.__chunks:
            return
        self.__loaded_chunks.append( chunk_pos.c() )

        # Spawn any entities within the chunk
        for pos in self.__chunks[ chunk_pos ]:

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

    # Loading a region loads chunks into memory, but by itself doesn't load them in
    def _load_region( self, region_pos ):

        # Do nothing if region is already loaded
        if ( region_pos in self.__loaded_regions ):
            return

        # Do nothing if file can't be loaded
        try:
            filename = f'rg_{ region_pos.x }_{ region_pos.y }.txt'
            region_file = open( self.__engine.get_path( f'/data/{ self._level_name }/{ filename }' ) ).read().split( '\n' )
        except FileNotFoundError:
            return

        self.__loaded_regions.append( region_pos.c() )

        # Load the objects into memory
        for line in [ line for line in region_file if line != '' ]:

            # If blank line, do nothing
            if len( line ) == 0:
                continue

            # Otherwise, create a block/entity at the listed positions
            # Split the line by spaces
            # The first token is the object ID, and the subsequent tokens
            # represent coordinate pairs at which the objects should be created
            line = line.split( ' ' )
            object_id = utils.o_id( line[0] )
            object_positions = [ V2( line[ i : i + 2 ] ).i() for i in range( 1, len( line ), 2 ) ]

            # Now, loop through coordinates and set the objects
            for obj_pos in object_positions:
                self._set_object( obj_pos, object_id )

    # Unloading a region frees up the memory it was using
    # This should only be used when no chunks within the region are loaded
    def _unload_region( self, region_pos ):

        # Do nothing if already unloaded
        if ( region_pos not in self.__loaded_regions ):
            return

        # Remove every chunk from memory
        chunk_positions = []
        for xx in range( region_pos.x * R_GRID, ( region_pos.x + 1 ) * R_GRID ):
            for yy in range( region_pos.y * R_GRID, ( region_pos.y + 1 ) * R_GRID ):
                chunk_positions.append( V2( xx, yy ) )

        for chunk_pos in chunk_positions:

            # Don't unload empty chunks
            if chunk_pos not in self.__chunks:
                continue

            # Remove all positions within the chunk
            for pos in self.__chunks[ chunk_pos ]:

                pos = utils.chunk_pos_to_block( chunk_pos, pos )

                # Remove position data from all dictionaries
                self.__objects.pop( pos )
                self.__object_meta.pop( pos )

            self.__chunks.pop( chunk_pos )

        self.__loaded_regions.remove( region_pos )
            
    # Only responsible for drawing blocks
    # Since enemies are their own objects, they're capable of drawing themselves
    # This is a little convoluted, but it's necessary for performance
    def draw( self ):

        self.__c_block.draw()

    # Set block/entity at target position
    def _set_object( self, pos, object_id ):

        # Initialize the object data
        self.__objects[ pos ] = object_id
        self.__object_meta[ pos ] = {}

        block_id = utils.obj_id_to_block( object_id )
        entity_id = utils.obj_id_to_entity( object_id )

        # Do any necessary block setup
        if ( block_id is not None ):
            if ( B_DRAW_MODES[ block_id ] in [ BDM_3VAR_OVERLAY, BDM_3VAR_REPLACE ] ):
                self.__object_meta[ pos ][ 'var' ] = random.randint( 0, 2 )
            else:
                self.__object_meta[ pos ][ 'var' ] = 0

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

    # Check whether an entity exists at a position
    def is_entity( self, pos ):

        try:
            return utils.obj_id_to_entity( self.__objects[ pos ] ) != None
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

        cursor_pos = self.__engine.get_world_cursor()
        print( 'Cursor in chunk', cursor_pos.fn( lambda a: int( a // ( GRID * C_GRID ) ) ) )

    # Getters/setters

    @property
    def controller( self ):
        return self._controller