from basic_imports import *
from bg_region_1 import *
from bg_region_2 import *

from drawer import *

# In charge of controlling in-game backgrounds and music
class RegionController:

    RG_UPDATE_INTERVAL = 0.5
    BG_UPDATE_INTERVAL = 1
    TRANSITION = 1
    X_LOOP = 4000

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.engine = self.controller.engine

        # Store the current region id
        self._region_id = -1

        # Backgrounds are referenced with their region ID
        # Only one background is loaded at a time
        # REGION_STRINGS and REGION_BGS are used to map a region ID to a class instance
        self.__active_bg = None

        # Also store a surface to cover up the bg
        self.__bg_cover = pygame.Surface( self.engine.screen_size.l(), pygame.SRCALPHA, 32 )
        self.__bg_cover.fill( ( 0, 0, 0, 0 ) )

        # Store the time since last update
        self.__rg_elapsed = self.RG_UPDATE_INTERVAL
        self.__bg_elapsed = 0
        self.__fade_in_elapsed = -1
        self.__fade_out_elapsed = -1

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.engine, LAYER_BACKGROUND, self.draw )

    # Update the current region and surface backgrounds
    # Both of these events run on a timer instead of being
    # executed every frame
    def update( self ):

        # Update transition timers before everything else so
        # they don't have delta_time added halfway through the event
        if self.__fade_out_elapsed >= 0:
            self.__fade_out_elapsed += self.engine.delta_time

        if self.__fade_in_elapsed >= 0:
            self.__fade_in_elapsed += self.engine.delta_time

        # Check if region should be switched
        # Only applies if no fading is in progress
        self.__rg_elapsed += self.engine.delta_time
        is_fading = self.__fade_out_elapsed >= 0 or self.__fade_in_elapsed >= 0
        if ( self.__rg_elapsed >= self.RG_UPDATE_INTERVAL and not is_fading ):

            # Reset the elapsed time for the next update
            # divmod() is used to get the remainder so when more than RG_UPDATE_INTERVAL
            # has passed, it can keep the extra bit instead of resetting it to 0
            _, self.__rg_elapsed = divmod( self.__rg_elapsed, self.RG_UPDATE_INTERVAL )

            # Get the region from the player
            # This can either return an ID or -1
            new_region_id = self.engine.get_instance( 'player' ).get_region()

            # Update the region if the new ID exists and isn't equal the current region
            if ( new_region_id != -1 and new_region_id != self.region_id ):
                self.set_region( new_region_id )

        # Perform update if more than BG_UPDATE_INTERVAL seconds has elapsed
        self.__bg_elapsed += self.engine.delta_time
        if ( self.__bg_elapsed >= self.BG_UPDATE_INTERVAL ):

            # Update all background, passing in the delta_time
            # since the last update
            if self.__active_bg is not None:
                self.__active_bg.update_surf( self.__bg_elapsed )

            # Reset the elapsed time for the next update
            _, self.__bg_elapsed = divmod( self.__bg_elapsed, self.BG_UPDATE_INTERVAL )
        
        # Check if backgrounds should be swapped out mid-transition
        if self.__fade_out_elapsed > self.TRANSITION:

            self.__fade_out_elapsed = -1
            self.__fade_in_elapsed = 0

            container = self
            self.__active_bg = eval( f'{ REGION_BGS[ self._region_id ] }( container )' )
        
        if self.__fade_in_elapsed > self.TRANSITION:
            self.__fade_in_elapsed = -1
            
    # Draw the currently loaded background (if one exists)
    def draw( self ):

        # If there are no backgrounds to draw, draw a single-colored surface
        if ( self.__active_bg is None ):
            
            self.__bg_cover.fill( ( 0, 0, 0, 255 ) )
            self.engine.draw_surface( self.__bg_cover, V2(), True )
            return

        # Get the surface of the active background
        bg = self.__active_bg.get_surf()

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

        # Draw a black surface over it during a fade in and fade out transition
        if ( self.__fade_out_elapsed >= 0 or self.__fade_in_elapsed >= 0 ):

            opacity = max( self.__fade_out_elapsed, self.__fade_in_elapsed ) / self.TRANSITION
            if self.__fade_in_elapsed >= 0:
                opacity = 1 - opacity
            self.__bg_cover.fill( ( 0, 0, 0, int( opacity * 255 ) ) )
            self.engine.draw_surface( self.__bg_cover, V2(), True )

    # Changes the currently active region
    def set_region( self, region_id ):

        self.engine.queue_music( self.TRANSITION, REGION_SONGS[ region_id ], volume = 0.4, fade_in = self.TRANSITION )
        self._region_id = region_id
        self.__fade_out_elapsed = 0

    # Getters/setters
    @property
    def controller( self ):
        return self._controller

    @property
    def region_id( self ):
        return self._region_id