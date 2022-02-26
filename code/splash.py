from basic_imports import *
from settings import *

class Splash ( Game_Object ):

    def __init__( self, engine ):

        super().__init__( engine, 'splash', 0 )

        # Load language files
        lang.load( engine )

        # Initialize fonts
        engine.create_bitmap_font( '/textures/font_1.png', 'main', space_width = 6 )

        # Apply settings
        SettingsController( self.engine ).apply_settings()

        # Time controls fade animation/room switch
        self._time = -1
        self._surf = pygame.transform.scale( self.engine.get_sprite( 'splash', V2() ), self.engine.screen_size.l() )

        # Intro music
        engine.play_music( 'mus_menu_1', loops = 0 )

    # Let time tick/check if room should switch
    def update( self ):

        self._time += self.engine.delta_time
        if ( self._time >= 6 ):
            self.engine.switch_room( 'frontend' )

        # Can skip by pressing space
        if ( self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.switch_room( 'frontend' )

    # Draw splash text with correct opacity
    def draw( self ):

        opacity = utils.clamp( 2.5 - abs( self._time - 2.5 ), 0, 1 )
        self._surf.set_alpha( opacity * 255 )
        self.engine.draw_surface( self._surf, self.engine.screen_size.c().d( 2 ), True, anchor = V2( 0.5, 0.5 ) )