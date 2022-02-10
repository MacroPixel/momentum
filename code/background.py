from basic_imports import *

# Allows deriving from to create custom backgrounds
# Stored in a Background_Container object, which allows
# specialized updating, drawing, and switching out of backgrounds
class Background ():

    def __init__( self, engine ):

        # Store the time since last update
        self.__time_elapsed = 0

        # Other variables
        self.pos = V2()

    # Update surfaces should be updated relatively infrequently
    # This function returns True every time that TIME_INTERVAL
    # seconds have passed since the last True return
    def is_update_interval( self ):

        # Perform update if more than TIME_INTERVAL seconds has elapsed
        self.__time_elapsed += self.engine.delta_time
        if ( self.__time_elapsed >= self.TIME_INTERVAL ):

            _, self.__time_elapsed = divmod( self.__time_elapsed, self.TIME_INTERVAL )
            return True

        return False

    # Anchors the position to the view
    def update_pos( self, surf_dimensions ):

        self.pos = self.engine.view_pos.c().s( surf_dimensions.c().d( 2 ) )