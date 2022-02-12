from basic_imports import *

# Allows deriving from to create custom backgrounds
# Stored in a Background_Container object, which allows
# specialized updating, drawing, and switching out of backgrounds
class Background ():

    # Interface class for background
    # __init__ should be called after everything is set up
    def __init__( self, container ):

        self.container = container
        self.engine = self.container.engine
        self.update_surf( 0 )

    # Called whenever the surface is intended to update
    # Called relatively infrequently to save on performance
    def update_surf( self, delta_time ):
        pass

    # Returns the current background surface
    def get_surf( self ):
        pass