import pygame
from .vector import *

class Sprite:

    def __init__( self, engine, surf, dimensions = V2( 1, 1 ) ):
        
        # Store a reference to the engine
        self.__engine = engine
        self.__zoom = self.__engine.view_zoom

        # Use the dimensions of the sprite divided by the # of subimages to get the size of a square
        dims = V2( surf.get_size() )
        self.square_count = V2( dimensions )
        self.square_size = dims.c().d( square_count )

        # Use the previous information to split the sprite up and append it to the sprite data
        self.__images = [ [ surf.subsurface( ( xx * self.square_size.x, yy * self.square_size.y, *self.square_size.l() ) ) for xx in range( self.square_count.x ) ]
            for yy in range( self.square_count.y ) ]

        # Store the scaled up version of each image
        self.__zoom_buffers = []
        for xx in range( self.square_count.x ):
            for yy in range( self.square_count.y ):
                self.__update_zoom_buffer(  )

    # Stores a version of the image scaled up by a factor of the engine's zoom level
    # This prevents it from having to repeatedly scale up the surface
    def update_zoom_buffer( self, frame ):

        # Ignore if already the correct size
        if ( self.__zoom == self.__engine.view_zoom ):
            return

        # Scale the source and store it
        self.__zoom_buffers
            
    # Return the surface of a particular subimage
    # Takes the view zoom of its parent surface into account 
    def get_surf( self ):
        
        # Update the scale of the surface
        self.__update_zoom_buffer()