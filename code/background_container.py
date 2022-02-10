from basic_imports import *

from bg_area_1 import *

# Holds, draws, and switches between all backgrounds
class Background_Container ( Game_Object ):

    TIME_INTERVAL = 1

    def __init__( self, engine ):

        super().__init__( engine, 'background_container', layer = LAYER_BACKGROUND )

        # Backgrounds are referenced with their region ID
        # Only one background can be loaded at once
        # (i.e. only one background at a time can update its surface)
        self.__bg_surfs = {}
        self.__bg_active = None

        # Store the time since last update
        self.__time_elapsed = 0

    # Surfaces should be updated relatively infrequently, so update_surf()
    # is only called once every TIME_INTERVAL seconds
    def update( self ):

        # Perform update if more than TIME_INTERVAL seconds has elapsed
        self.__time_elapsed += self.engine.delta_time
        if ( self.__time_elapsed >= self.TIME_INTERVAL ):

            # Update all background, passing in the delta_time
            # since the last update
            if self.__bg_active is not None:
                self.__bg_surfs[ self.__bg_active ].update_surf( self.__time_elapsed )

            # Reset the elapsed time for the next update
            # divmod() is used to get the remainder so when more than TIME_INTERVAL
            # has passed, it can keep the extra bit instead of resetting it to 0
            _, self.__time_elapsed = divmod( self.__time_elapsed, self.TIME_INTERVAL )

    # Draw any visible backgrounds
    # Because of fading in/out, multiple backgrounds will sometimes be drawn at once
    def draw( self ):

        # Exit if there are no backgrounds to draw
        if ( self.__bg_active is None ):
            return

        # Get the surface of the active background
        