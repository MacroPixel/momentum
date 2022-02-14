from basic_imports import *
import random

# Contained within/controlled by LevelController
# Block storing/drawing
# Blocks aren't actually objects, they're only entries in an array
class BlockController():

    def __init__( self, level_controller ):

        # Basic block data
        # Initialized with a function to allow easy resetting
        self.reset_data()

        # Parent objects
        self._level_controller = level_controller
        self.__engine = self.level_controller.controller.engine
    
    # Initially creates local data; can also be used to reset data
    def reset_data( self ):

        self.__chunk_buffers = {}
            
    # Iterate through/draw all blocks
    # Blocks are drawn based off of chunk buffers stored in memory
    def draw( self ):

        # Loop through every loaded chunk and draw it
        for chunk_pos in self.__chunk_buffers:
            self.__engine.draw_surface( self.__chunk_buffers[ chunk_pos ], chunk_pos.c().m( C_GRID * GRID ), False, buffer_key = chunk_pos )

    # Creates a surface for easy-drawing
    def create_buffer( self, chunk_pos ):
        
        # Initialize it with an empty surface
        surf = pygame.Surface( ( C_GRID * GRID, C_GRID * GRID ), pygame.SRCALPHA, 32 )
        self.__chunk_buffers[ chunk_pos.c() ] = surf

        # Draw every block onto it
        for xx in range( C_GRID ):
            for yy in range( C_GRID ):
                
                block_pos = utils.chunk_pos_to_block( chunk_pos, V2( xx, yy ) )

                if ( self.level_controller.is_block( block_pos ) ):
                    surf.blit( self.render_block( block_pos ), ( xx * GRID, yy * GRID ) )

    # Deletes a surface when it's no longer needed
    def delete_buffer( self, chunk_pos ):

        self.__chunk_buffers.pop( chunk_pos )
        self.__engine.zoom_buffer_remove( chunk_pos )

    def reset_buffers( self ):

        for chunk_pos in self.__chunk_buffers.copy():
            self.delete_buffer( chunk_pos )

    # Returns either None or a surface representing a block sprite
    def render_block( self, block_pos ):

        # Only bother with a texture if a block exists here
        if not self.level_controller.is_block( block_pos ):
            return None

        # Generate variant based off object type
        block_id = self.level_controller.get_block_type( block_pos )
        variant = random.randint( 0, B_DRAW_VARIANTS[ block_id ] - 1 )

        # Start with the sprite's base image
        sprite_id = B_TEXTURES[ block_id ]
        surf = self.__engine.get_sprite( sprite_id, V2( variant, 0 ) ).copy()

        # Find the binary representation of the block's neighbors
        # An outline only appears if there's no neighbor along a certain side
        neighbors = [ False for i in range( 8 ) ]
        offsets = ( ( 1, 0 ), ( 1, -1 ), ( 0, -1 ), ( -1, -1 ), ( -1, 0 ), ( -1, 1 ), ( 0, 1 ), ( 1, 1 ) )
        regions = ( ( GRID / 2, 0 ), ( 0, 0 ), ( 0, GRID / 2 ), ( GRID / 2, GRID / 2 ) )

        # Check for adjacent blocks
        # (0 = right, 2 = up, 4 = left, 6 = down)
        # (1 = up/right, 3 = up/left, you get the idea)
        for i in range( 0, 8 ):
            
            # Default to not connecting
            neighbors[ i ] = False
            other_pos = block_pos.c().a( offsets[i] )

            # Exit if no block
            if ( not self.level_controller.is_block( other_pos ) ):
                continue
            other_id = self.level_controller.get_block_type( other_pos )

            # Automatically connect if both block types are the same
            if ( block_id == other_id ):
                neighbors[ i ] = True
                continue
            
            # Connect if both types are connectable
            if ( utils.b_string( block_id ) not in B_NO_CONNECT and utils.b_string( other_id ) not in B_NO_CONNECT ):
                neighbors[ i ] = True
                continue

            # Otherwise, don't connect
            # (Just do nothing since neighbors[i] is already false)

        # Draw corners/line intersections
        draw_mode = B_DRAW_MODES[ block_id ]
        for i in range( 0, 8, 2 ):

            corner_neighbors = [ neighbors[ i ], neighbors[ ( i + 1 ) % 8 ], neighbors[ ( i + 2 ) % 8 ] ]

            if ( corner_neighbors == [ False, False, False ] or corner_neighbors == [ False, True, False ] ):

                if draw_mode == BDM_OVERLAY:

                    corner_surf = self.__engine.get_sprite( sprite_id, V2( variant, 3 ) ).copy()
                    corner_surf = pygame.transform.rotate( corner_surf, ( i + 6 ) * 45 )
                    surf.blit( corner_surf, ( 0, 0 ) )

                elif draw_mode == BDM_REPLACE:

                    corner_surf = self.__engine.get_sprite( sprite_id, V2( variant, 4 ) ).copy()
                    rect = ( regions[ i // 2 ][0], regions[ i // 2 ][1], GRID / 2, GRID / 2 )
                    surf = utils.stitch_sprites( surf, corner_surf, rect )

            elif ( corner_neighbors == [ True, False, True ] ):

                if draw_mode == BDM_OVERLAY:

                    corner_surf = self.__engine.get_sprite( sprite_id, V2( variant, 1 ) ).copy()
                    corner_surf = pygame.transform.rotate( corner_surf, ( i + 6 ) * 45 )
                    surf.blit( corner_surf, ( 0, 0 ) )

                elif draw_mode == BDM_REPLACE:

                    corner_surf = self.__engine.get_sprite( sprite_id, V2( variant, 1 ) ).copy()
                    rect = ( regions[ i // 2 ][0], regions[ i // 2 ][1], GRID / 2, GRID / 2 )
                    surf = utils.stitch_sprites( surf, corner_surf, rect )

        # Draw outlines
        for i in range( 0, 8, 2 ):

            right_neighbors = [ neighbors[ i ], neighbors[ ( i + 2 ) % 8 ] ]

            if ( right_neighbors[0] != right_neighbors[1] ):

                if draw_mode == BDM_OVERLAY:

                    line_surf = self.__engine.get_sprite( sprite_id, V2( variant, 2 ) ).copy()
                    line_surf = pygame.transform.flip( line_surf, False, right_neighbors[1] )
                    if right_neighbors[0]:
                        line_surf = pygame.transform.rotate( line_surf, ( i + 6 ) * 45 )
                    else:
                        line_surf = pygame.transform.rotate( line_surf, ( i + 4 ) * 45 )
                    surf.blit( line_surf, ( 0, 0 ) )

                elif draw_mode == BDM_REPLACE:

                    subimage = 2 if ( ( i % 4 == 0 ) != right_neighbors[0] ) else 3
                    line_surf = self.__engine.get_sprite( sprite_id, V2( variant, subimage ) ).copy()
                    rect = ( regions[ ( i // 2 ) % 4 ][0], regions[ ( i // 2 ) % 4 ][1], GRID / 2, GRID / 2 )
                    surf = utils.stitch_sprites( surf, line_surf, rect )

        return surf

    # Getters/setters
    @property
    def level_controller( self ):
        return self._level_controller