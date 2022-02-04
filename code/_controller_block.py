from basic_imports import *

# Contained within/controlled by controller
# Handles block storing/drawing
# Blocks aren't actually objects, they're only entries in an array
class BlockController():

    def __init__( self, filepath ):

        # Block data
        self.__blocks = {}
        self.__block_meta = {}
        self.__chunks = {}
        self.__chunk_buffers = {}
        self.__loaded_chunks = []

        # Initialize block data
        self.load_level( filepath )

    # Loads the level data into memory
    def load_level( self, filepath ):

        level_data = open( filepath ).read().split( '\n' )

        # Group the data into chunks (denoted by "* X:Y")
        # This is done solely to aid with drawing the blocks in
        self.__blocks = {}
        self.__chunks = {}
        self.__chunk_buffers = {}
        self.__loaded_chunks = []
        current_chunk = ''
        for line in level_data:

            # Switch chunk
            if len( line ) == 0:
                pass

            elif line[0] == '*':
                try:
                    current_chunk = utils.vec_to_str( V2( line.split( '* ' )[1].split( ':' ) ) )
                    self.__chunks[ current_chunk ] = []
                except ( ValueError, IndexError ):
                    raise RuntimeError( 'Invalid chunk format' )

            # Create objects under chunk
            else:

                # If chunk isn't active
                if ( current_chunk == '' ):
                    raise RuntimeError( 'No chunk was specified' )

                # Otherwise, store the block name & loop through coordinates
                block_id = B_STRINGS.index( line.split( ' ' )[0] )
                for i in range( 1, len( line.split( ' ' ) ), 2 ):

                    # Create block & store position under current chunk
                    chunk_coords = utils.str_to_vec( current_chunk ).m( C_GRID )
                    temp_pos = V2( line.split( ' ' )[ i:i + 2 ] ).i().a( chunk_coords )
                    self.set_block( temp_pos, block_id )
                    self.__chunks[ current_chunk ].append( utils.vec_to_str( temp_pos ) )

    # Recreates the level data from a PNG image
    def rewrite_level( self, controller ):

        # Load the PNG into memory
        block_surf = pygame.image.load( controller.engine.get_path( '/data/blocks.png' ) )

        keys = {} # The position of every block in the PNG
        origin = V2( 0, 0 ) # Where the player spawns

        # Loop through all the pixels in the PNG
        for xx in range( block_surf.get_width() ):
            for yy in range( block_surf.get_height() ):

                pos = V2( xx, yy )

                # Create the player if the pixel is white
                if block_surf.get_at( pos.l() ) == ( 255, 255, 255, 255 ):
                    origin = pos

                # Otherwise, create the appropriate block based on color
                else:
                    for i in range( 1, B_TOTAL ):
                        if block_surf.get_at( pos.l() ) == B_COLORS[i]:
                            keys[ utils.vec_to_str( pos ) ] = i

        # Store the real position of every block,
        # relative to the origin instead of top-left of image
        chunks = {}

        for pos in keys:

            new_pos = utils.str_to_vec( pos ).s( origin )
            chunk_pos = new_pos.c().d( C_GRID ).fn( lambda a: int( floor( a ) ) )
            chunk_str = utils.vec_to_str( chunk_pos )

            if chunk_str not in chunks:
                chunks[ chunk_str ] = {}
            chunks[ chunk_str ][ utils.vec_to_str( new_pos.c().s( chunk_pos.c().m( C_GRID ) ) ) ] = keys[ pos ]

        # Actually write to the file
        file = open( controller.engine.get_path( '/data/blocks.txt' ), 'w' )
        for chunk in chunks:

            file.write( f'* { chunk }\n' )

            for block_pos in chunks[ chunk ]:

                file.write( f'{ B_STRINGS[ chunks[ chunk ][ block_pos ] ] } { block_pos.replace( ":", " " ) }\n' )
            
    # Iterate through/draw all blocks
    # Blocks are drawn based off of chunk buffers stored in memory
    def draw( self, engine, controller ):

        # Draw chunks within the proper bound
        # Bound is specified in blocks offset from view center (via RENDER_BOUNDS)
        bound_1 = engine.view_pos.c().fn( lambda a: round( a / GRID / C_GRID ) ).s( RENDER_BOUNDS )
        bound_2 = engine.view_pos.c().fn( lambda a: round( a / GRID / C_GRID ) ).a( RENDER_BOUNDS )

        for xx in range( bound_1.x, bound_2.x + 1 ):
            for yy in range( bound_1.y, bound_2.y + 1 ):

                chunk_pos = V2( xx, yy )

                # Make sure the chunk exists
                if utils.vec_to_str( chunk_pos ) not in self.__chunks:
                    continue

                # Create the chunk if it doesn't exist
                if ( utils.vec_to_str( chunk_pos ) not in self.__chunk_buffers ):
                    self.load_chunk( chunk_pos, engine )

                engine.draw_surface( self.__chunk_buffers[ utils.vec_to_str( chunk_pos ) ], chunk_pos.c().m( C_GRID * GRID ), False )

    # Creates a surface for easy-drawing
    def load_chunk( self, chunk_pos, engine ):
        
        # Initialize it with an empty surface
        surf = pygame.Surface( ( C_GRID * GRID, C_GRID * GRID ), pygame.SRCALPHA, 32 )
        self.__chunk_buffers[ utils.vec_to_str( chunk_pos ) ] = surf

        # Draw every block onto it
        for xx in range( C_GRID ):
            for yy in range( C_GRID ):
                
                block_pos = chunk_pos.c().m( C_GRID ).a( xx, yy )

                if ( self.is_block( block_pos ) ):
                    surf.blit( self.render_block( block_pos, engine ), ( xx * GRID, yy * GRID ) )

    # Returns either None or a surface representing a block sprite
    def render_block( self, block_pos, engine ):

        # Only bother with a texture if a block exists here
        if not self.is_block( block_pos ):
            return None

        # Start with the sprite's base image
        sprite_id = B_TEXTURES[ self.get_block_type( block_pos ) ]
        variant = self.__block_meta[ utils.vec_to_str( block_pos ) ][ 'var' ]
        draw_mode = B_DRAW_MODES[ self.get_block_type( block_pos ) ]
        surf = engine.get_sprite( sprite_id, V2( variant, 0 ) ).copy()

        # Find the binary representation of the block's neighbors
        # An outline only appears if there's no neighbor along a certain side
        neighbors = [ False for i in range( 8 ) ]
        offsets = ( ( 1, 0 ), ( 1, -1 ), ( 0, -1 ), ( -1, -1 ), ( -1, 0 ), ( -1, 1 ), ( 0, 1 ), ( 1, 1 ) )
        regions = ( ( GRID / 2, 0 ), ( 0, 0 ), ( 0, GRID / 2 ), ( GRID / 2, GRID / 2 ) )

        # Check for adjacent blocks
        # (0 = right, 2 = up, 4 = left, 6 = down)
        # (1 = up/right, 3 = up/left, you get the idea)
        for i in range( 0, 8 ):
            neighbors[ i ] = self.is_block( block_pos.c().a( offsets[i] ) )

        # Draw corners/line intersections
        for i in range( 0, 8, 2 ):

            corner_neighbors = [ neighbors[ i ], neighbors[ ( i + 1 ) % 8 ], neighbors[ ( i + 2 ) % 8 ] ]

            if ( corner_neighbors == [ False, False, False ] or corner_neighbors == [ False, True, False ] ):

                if draw_mode in [ BDM_SINGLE_OVERLAY, BDM_DEF_OVERLAY ]:

                    corner_surf = engine.get_sprite( sprite_id, V2( 0, 3 ) ).copy()
                    corner_surf = pygame.transform.rotate( corner_surf, ( i + 6 ) * 45 )
                    surf.blit( corner_surf, ( 0, 0 ) )

                elif draw_mode == BDM_DEF_REPLACE:

                    corner_surf = engine.get_sprite( sprite_id, V2( variant, 4 ) ).copy()
                    rect = ( regions[ i // 2 ][0], regions[ i // 2 ][1], GRID / 2, GRID / 2 )
                    surf = stitch_sprites( surf, corner_surf, rect )

            elif ( corner_neighbors == [ True, False, True ] ):

                if draw_mode in [ BDM_SINGLE_OVERLAY, BDM_DEF_OVERLAY ]:

                    corner_surf = engine.get_sprite( sprite_id, V2( 0, 1 ) ).copy()
                    corner_surf = pygame.transform.rotate( corner_surf, ( i + 6 ) * 45 )
                    surf.blit( corner_surf, ( 0, 0 ) )

                elif draw_mode == BDM_DEF_REPLACE:

                    corner_surf = engine.get_sprite( sprite_id, V2( variant, 1 ) ).copy()
                    rect = ( regions[ i // 2 ][0], regions[ i // 2 ][1], GRID / 2, GRID / 2 )
                    surf = stitch_sprites( surf, corner_surf, rect )

        # Draw outlines
        for i in range( 0, 8, 2 ):

            right_neighbors = [ neighbors[ i ], neighbors[ ( i + 2 ) % 8 ] ]

            if ( right_neighbors[0] != right_neighbors[1] ):

                if draw_mode in [ BDM_SINGLE_OVERLAY, BDM_DEF_OVERLAY ]:

                    line_surf = engine.get_sprite( sprite_id, V2( 0, 2 ) ).copy()
                    line_surf = pygame.transform.flip( line_surf, False, right_neighbors[1] )
                    if right_neighbors[0]:
                        line_surf = pygame.transform.rotate( line_surf, ( i + 6 ) * 45 )
                    else:
                        line_surf = pygame.transform.rotate( line_surf, ( i + 4 ) * 45 )
                    surf.blit( line_surf, ( 0, 0 ) )

                elif draw_mode == BDM_DEF_REPLACE:

                    subimage = 2 if ( ( i % 4 == 0 ) != right_neighbors[0] ) else 3
                    line_surf = engine.get_sprite( sprite_id, V2( 0, subimage ) ).copy()
                    rect = ( regions[ ( i // 2 ) % 4 ][0], regions[ ( i // 2 ) % 4 ][1], GRID / 2, GRID / 2 )
                    surf = stitch_sprites( surf, line_surf, rect )

        return surf

    # Either changes a block or removes it (by setting it to B_NULL)
    def set_block( self, pos, block_type ):

        # Convert position & alter array
        pos = V2( pos )
        if block_type == B_NULL:

            if self.is_block( pos ):

                self.__blocks.pop( utils.vec_to_str( pos ) )
                self.__block_meta.pop( utils.vec_to_str( pos ) )

        else:

            # Initialize the block data
            self.__blocks[ utils.vec_to_str( pos ) ] = block_type
            self.__block_meta[ utils.vec_to_str( pos ) ] = {}

            # Do any further setup
            if ( B_DRAW_MODES[ block_type ] in [ BDM_DEF_OVERLAY, BDM_DEF_REPLACE ] ):
                self.__block_meta[ utils.vec_to_str( pos ) ][ 'var' ] = random.randint( 0, 2 )
            else:
                self.__block_meta[ utils.vec_to_str( pos ) ][ 'var' ] = 0

    # Check whether a block exists at a position
    def is_block( self, pos ):

        return utils.vec_to_str( pos ) in self.__blocks

    # Get the block type of a position
    # !!! WILL throw error if there isn't a block there
    def get_block_type( self, pos ):

        return self.__blocks[ utils.vec_to_str( pos ) ]

    # Performs an operation on the block the player is hovering over
    def block_debug( self, cursor_pos, view ):

        block_pos = V2( cursor_pos ).a( view ).fn( lambda a: int( floor( a / GRID ) ) )

        if ( self.is_block( block_pos ) ):

            # Find the binary representation of the block's neighbors
            # An outline only appears if there's no neighbor along a certain side
            neighbors = [ False for i in range( 8 ) ]
            offsets = ( ( 1, 0 ), ( 1, 1 ), ( 0, 1 ), ( -1, 1 ), ( -1, 0 ), ( -1, -1 ), ( 0, -1 ), ( 1, -1 ) )

            # Check for adjacent blocks
            # (0 = right, 2 = down, 4 = left, 6 = up)
            # (1 = down/right, 3 = down/left, you get the idea)
            for i in range( 0, 8 ):
                neighbors[ i ] = self.is_block( block_pos.c().a( offsets[i] ) )

            print( neighbors )