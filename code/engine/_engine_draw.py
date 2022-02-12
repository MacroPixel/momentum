import pygame
from .vector import *
from .bitmap_font import *

# Initially loads the sprites into memory
# Should only be called once
def _load_sprites( self ):

    if ( len( self._Engine__sprites ) != 0 ):
        raise ValueError( 'Sprites have already been initialized' )

    spr_file = open( self.get_path( '/textures/list.txt' ) ).read().split( '\n' )

    # Iterate through every line in the sprite file
    # Sprites are listed as follows:
    # [name] = [relative filepath] [scale]:[# vertical subimages]:[# horizontal subimages]
    for line in spr_file:

        # Parse through the data within the line of text
        internal_name, line = line.split( ' = ' )
        filename, line = line.split( ' ' )
        dimensions = [ int( a ) for a in line.split( ':' ) ]

        # Load the image and transform it based on the data in the file line
        surface = pygame.image.load( self.get_path( '/textures/' + filename ) )
        surface = pygame.transform.scale( surface, V2( surface.get_size() ).l() )

        # Use the dimensions of the sprite divided by the # of subimages to get the size of a square
        dims = V2( surface.get_size() )
        square_count = V2( dimensions )
        square_size = dims.c().d( square_count )

        # Use the previous information to split the sprite up and append it to the sprite data
        self._Engine__sprites[ internal_name ] = [ [ surface.subsurface( ( xx * square_size.x, yy * square_size.y, *square_size.l() ) ) for xx in range( square_count.x ) ]
            for yy in range( square_count.y ) ]

def draw_line( self, pos_a, pos_b, is_ui, color, **kwargs ):

    # "is_ui" specifies whether to use game coordinates or UI coordinates
    # Game coords are measured in blocks and UI coords are measured in pixels
    if is_ui:
        pos_a = pos_a.c()
        pos_b = pos_b.c()
    else:
        pos_a = self.to_screen_coord( pos_a )
        pos_b = self.to_screen_coord( pos_b )

    # Draw antialiased line if told to
    if 'is_aa' in kwargs and kwargs[ 'is_aa' ]:
        pygame.draw.aaline( self._Engine__screen, color, pos_a.l(), pos_b.l() )
    # Otherwise, draw jagged line
    else:
        pygame.draw.line( self._Engine__screen, color, pos_a.l(), pos_b.l() )

# Shortcut for blitting transformed surface onto screen
# Every other draw function (except draw_line) leads to this one
def draw_surface( self, surf, pos, is_ui, **kwargs ):

    # "is_ui" specifies whether to use game coordinates or UI coordinates
    # Game coords are measured in blocks and UI coords are measured in pixels
    if is_ui:
        pos = pos.c()
    else:
        pos = self.to_screen_coord( pos )

    # Scale based on zoom level (doesn't affect UI)
    # Can also be disabled via 'fixed_size = True'
    if not ( is_ui or ( 'fixed_size' in kwargs and kwargs[ 'fixed_size' ] ) ):

        # Use an already-existing surface if possible
        if 'buffer_key' in kwargs and kwargs[ 'buffer_key' ] in self._Engine__zoom_buffer:
            surf = self._Engine__zoom_buffer[ kwargs[ 'buffer_key' ] ]
        else:
            surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( self.view_zoom ).l() )

    # Store the scaled version of this surface in memory if told to
    # The caller of the function is in charge of providing a unique key
    if ( 'buffer_key' in kwargs and kwargs[ 'buffer_key' ] not in self._Engine__zoom_buffer ):
        self._Engine__zoom_buffer[ kwargs[ 'buffer_key' ] ] = surf

    # Check each transformation argument to see if sprite needs to be modified
    if ( 'scale' in kwargs ):
        surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( kwargs[ 'scale' ] ).l() )
    if ( 'flip' in kwargs ):
        surf = pygame.transform.flip( surf, kwargs[ 'flip' ].x == -1, kwargs[ 'flip' ].y == -1 )
    if ( 'rotation' in kwargs ):
        surf = pygame.transform.rotate( surf, kwargs[ 'rotation' ] )

    # Shift the position based off of the anchor
    anchor = V2() if 'anchor' not in kwargs else kwargs[ 'anchor' ]
    pos.s( anchor.c().m( surf.get_size() ) )

    # Draw the modified surface
    self._Engine__screen.blit( surf, pos.l() )

# Uses pre-defined surface
def draw_sprite( self, sprite_id, frame, pos, is_ui, **kwargs ):

    sprite_surf = self._Engine__sprites[ sprite_id ][ frame.x ][ frame.y ]
    self.draw_surface( sprite_surf, pos, is_ui, **kwargs )

# Draws non-bitmap text onto the screen
def draw_text( self, text, font, pos, is_ui, color = ( 255, 255, 255 ), **kwargs ):

    text_surf = self._Engine__fonts[ font ].render( text, True, color )
    self.draw_surface( text_surf, pos, is_ui, **kwargs )

# Draws bitmap text (requires bitmap font)
def draw_text_bitmap( self, text, bitmap_font, scale, pos, is_ui, color = ( 255, 255, 255 ), sep = 1, **kwargs ):

    text_surf = self._Engine__bitmap_fonts[ bitmap_font ].render( text, scale, color, sep )

    # Change the color if necessary (from reddit.com/r/pygame/comments/hprkpr/how_to_change_the_color_of_an_image_in_pygame/)
    if ( color != ( 255, 255, 255 ) ):
        text_array = pygame.PixelArray( text_surf )
        text_array.replace( ( 255, 255, 255, 255 ), ( *color, 255 ) )
        del text_array

    self.draw_surface( text_surf, pos, is_ui, **kwargs )

# Converts game coordinates to screen coordinates
# Basically shifts it relative to view
def to_screen_coord( self, world_pos ):

    # zoomed_position = ( world_position - center_position ) * zoom_level
    zoomed_pos = world_pos.c().s( self.view_pos ).m( self.view_zoom ).i()

    # screen_position = zoomed_position + half_size
    screen_pos = zoomed_pos.a( self.screen_size.c().d( 2 ) )

    return screen_pos

# Undoes to_screen_coord
def to_world_coord( self, screen_pos ):

    # zoomed_position = screen_position - half_size
    zoomed_pos = screen_pos.c().s( self.screen_size.c().d( 2 ) )

    # world_position = ( zoomed_position / zoom_level ) + center_position
    world_pos = zoomed_pos.d( self.view_zoom ).a( self.view_pos )

    return world_pos

# Removes a sprite with a specific key from the zoom buffer
def zoom_buffer_remove( self, key ):

    self._Engine__zoom_buffer.pop( key )

# Returns a sprite surface for other objects to use
def get_sprite( self, sprite_id, frame ):

    return self._Engine__sprites[ sprite_id ][ frame.x ][ frame.y ]

# Creates a font under the name 'name:size'
# Loads it from an external .ttf or .otf file
def create_font( self, filepath, name, size ):

    self._Engine__fonts[ f'{ name }:{ size }' ] = pygame.font.Font( self.get_path( filepath ), size )

# Creates a bitmap font from a .PNG
def create_bitmap_font( self, filepath, name, space_width = None ):

    self._Engine__bitmap_fonts[ name ] = Bitmap_Font( self.get_path( filepath ), space_width = space_width )