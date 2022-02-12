from basic_imports import *
from bg_area_1 import *

# Holds, draws, and switches between all backgrounds
class Background_Container ( Game_Object ):

    TIME_INTERVAL = 1
    X_LOOP = 4000

    def __init__( self, engine ):

        super().__init__( engine, 'background_container', layer = LAYER_BACKGROUND )

        # Backgrounds are referenced with their region ID
        # Only one background can be loaded at once
        # (i.e. only one background at a time can update its surface)
        # AREA_STRINGS and BG_CLASSES are used to map a region ID to a class instance
        self.__backgrounds = { rg_str: eval( f'{ bg_obj }( self )', locals().update( { 'self': self } ) ) for rg_str, bg_obj in zip( AREA_STRINGS, BG_CLASSES ) }
        self.__active_bg = None

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
            if self.__active_bg is not None:
                self.__backgrounds[ self.__active_bg ].update_surf( self.__time_elapsed )

            # Reset the elapsed time for the next update
            # divmod() is used to get the remainder so when more than TIME_INTERVAL
            # has passed, it can keep the extra bit instead of resetting it to 0
            _, self.__time_elapsed = divmod( self.__time_elapsed, self.TIME_INTERVAL )

    # Changes the currently active background
    def set_active( self, region_id ):

        self.__active_bg = region_id

    # Draw any visible backgrounds
    # Because of fading in/out, multiple backgrounds will sometimes be drawn at once
    def draw( self ):

        # Exit if there are no backgrounds to draw
        if ( self.__active_bg is None ):
            return

        # Get the surface of the active background
        bg = self.__backgrounds[ self.__active_bg ].get_surf()

        # Derive the position from the view
        # It's always vertically-centered on the view, but it
        # loops horizontally once every X_LOOP pixels
        pos = self.engine.view_pos.c()
        offset_x = divmod( pos.x, self.X_LOOP )[1] / self.X_LOOP
        pos.x = ( pos.x - offset_x * bg.get_width() )

        # Draw it an many times as necessary to cover the screen
        # Oscillates between drawing left of view and right of view
        min_x = self.engine.view_bound_min.x
        max_x = self.engine.view_bound_max.x
        x_order = [ 0, 1, -1, 2, -2 ]

        # Draw duplicates of background to avoid gaps
        # Only draws in regions that overlap the screen's x coords
        for xx in x_order:

            left_bound = pos.x + xx * bg.get_width()
            right_bound = pos.x + ( xx + 1 ) * bg.get_width()

            if ( min_x < right_bound and max_x > left_bound ):
                
                self.engine.draw_surface( bg, pos.c().a( xx * bg.get_width(), 0 ), False, buffer_key = self.__active_bg, anchor = V2( 0, 0.5 ) )