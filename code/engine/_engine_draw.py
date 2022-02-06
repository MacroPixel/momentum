import pygame
from .vector import *

# Converts game coordinates to screen coordinates
# Basically shifts it relative to view
def __to_screen_coord( self, pos ):

    # zoomed_position = ( real_position - center_position ) * zoom_level
    zoomed_pos = pos.s( self.view_pos.c() ).m( self.view_zoom ).i()

    # screen_position = zoomed_position + half_size
    screen_pos = zoomed_pos.a( self.screen_size.c().d( 2 ) )

    return screen_pos

# Shortcut for blitting transformed surface onto screen
# Every other draw function leads to this one
def draw_surface( self, surf, pos, is_ui, scale = None, flip = None, anchor = V2( 0, 0 ), no_store = False ):

    surf_hash = hash( surf )

    # "is_ui" specifies whether to use game coordinates or UI coordinates
    # Game coords are measured in blocks and UI coords are measured in pixels
    if is_ui:
        pass
    else:
        pos = __to_screen_coord( self, pos )

    # Scale based on zoom level (doesn't affect UI)
    if not is_ui:

        # Use an already-existing surface if possible
        if not no_store and surf_hash in self._Engine__zoom_buffer:
            surf = self._Engine__zoom_buffer[ surf_hash ]
        else:
            surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( self.view_zoom ).l() )

    # Store the scaled version of this surface in memory (unless told not to)
    if ( not no_store and surf not in self._Engine__zoom_buffer ):
        self._Engine__zoom_buffer[ surf_hash ] = surf

    # Check each transformation argument to see if sprite needs to be modified
    if ( scale is not None ):
        surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( scale ).l() )
    if ( flip is not None ):
        surf = pygame.transform.flip( surf, flip.x == -1, flip.y == -1 )

    # Shift the position based off of the anchor
    pos.s( anchor.c().m( surf.get_size() ) )

    # Draw the modified surface
    self._Engine__screen.blit( surf, pos.l() )

# Uses pre-defined surface
def draw_sprite( self, sprite_id, frame, pos, is_ui, scale = None, flip = None, anchor = V2( 0, 0 ), no_store = False ):

    sprite_surf = self._Engine__sprites[ sprite_id ][ frame.x ][ frame.y ]
    self.draw_surface( sprite_surf, pos, is_ui, scale, flip, anchor )

# Shortcut for blitting text to the screen
# Passes the surface into draw_surface instead of drawing it from the function
def draw_text( self, text, font, pos, is_ui, color = ( 255, 255, 255 ), scale = None, flip = None, anchor = V2( 0, 0 ), no_store = False ):

    text_surf = self._Engine__fonts[ font ].render( text, True, color )
    self.draw_surface( text_surf, pos, is_ui, scale, flip, anchor )