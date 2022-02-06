import pygame
from .vector import *
from math import floor

class Bitmap_Font:

    ASCII = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

    def __init__( self, filepath, space_width = None ):

        # It's assumed that the file is 16x6 grid of ASCII characters
        # For each one of these characters, it finds its width when
        # transparency is excluded
        source_surf = pygame.image.load( filepath )
        self._char_size = V2( source_surf.get_size() ).d( 16, 6 ).i()

        # For each character, store its cropped surface
        # Space is a special case, so it isn't stored
        self.__char_surfs = {}
        for i in range( 33, 127 ):

            # Store the surface for the character
            i_prime = i - 32
            temp_surf = source_surf.subsurface( ( ( i_prime % 16 ) * self.char_size.x, floor( i_prime / 16 ) * self.char_size.y, *self.char_size.l() ) ).copy()

            # The width matches the x-coordinate of the rightmost non-transparent pixel + 1
            width = self.char_size.x
            for x in range( width - 1, -1, -1 ):

                # Preemptively update the width
                width = x + 1

                # Check if any pixel is non-transparent
                is_not_transparent = len( [ True for y in range( self.char_size.y ) if temp_surf.get_at( ( x, y ) )[3] != 0 ] ) != 0

                # If we found a non-transparent pixel, then the current width is correct
                # We can then exit the loop
                if ( is_not_transparent ):
                    break

            # Trim the surface down, and store it
            temp_surf = temp_surf.subsurface( ( 0, 0, width, self.char_size.y ) ).copy()
            self.__char_surfs[ self.ASCII[ i_prime - 1 ] ] = temp_surf

        # The space width (unsurprisingly) determines the width of a space
        # It can be changed, but defaults to the max width of a character
        self._space_width = self.char_size.x if space_width is None else max( 0, min( space_width, self.char_size.x ) )

    # Returns a surface with the inputted text rendered onto it
    # Line breaks are not currently supported
    def render( self, text, scale, color, sep = 1 ):

        # Find the total width of the surface
        # First, find the total width of all the characters combined
        # Character width defaults to max if not in list
        output_width = sum( [ self.get_char_surf( char ).get_width() for char in text ] )

        # Then, account for the separator between every character
        output_width += sep * ( len( text ) - 1 )

        # Iterate through every character and draw it onto a surface
        output_surf = pygame.Surface( ( output_width, self.char_size.y ), pygame.SRCALPHA, 32 )
        current_x = 0
        for char in text:

            char_surf = self.get_char_surf( char )
            output_surf.blit( char_surf, ( current_x, 0 ) )
            current_x += ( char_surf.get_width() + sep )

        return pygame.transform.scale( output_surf, ( output_surf.get_width() * scale, output_surf.get_height() * scale ) )

    # Gets the stored surface for a character
    # Returns a max-sized transparent surface if not found
    def get_char_surf( self, char ):

        return ( self.__char_surfs[ char ] if char in self.__char_surfs else pygame.Surface( ( self.space_width, self.char_size.y ), pygame.SRCALPHA, 32 ) )

    # Getters/setters
    @property
    def char_size( self ):
        return self._char_size.c()

    @property
    def space_width( self ):
        return self._space_width