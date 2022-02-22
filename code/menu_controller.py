from basic_imports import *
from settings import *

class Menu_Controller ( Game_Object ):

    def __init__( self, engine ):

        super().__init__( engine, 'menu_controller', layer = 1 )

        # Play menu song
        self.engine.play_music( 'mus_menu_2' )

        # Load settings into memory
        self._settings_obj = SettingsController( self.engine )
        self._is_viewing_settings = False

    def update( self ):
        
        # Goto main room if button is pressed
        if ( not self._is_viewing_settings and self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.switch_room( 'main' )

        # Quit if escape is pressed
        if ( not self._is_viewing_settings and self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self.engine.close_app()

        # Go to/exit settings menu
        if ( not self._is_viewing_settings and self.engine.get_key( pygame.K_s, 1 ) ):
            self._is_viewing_settings = True
        elif ( self._is_viewing_settings and self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self._is_viewing_settings = False

        # Cycle through settings menu
        if ( self._is_viewing_settings ):
            self._settings_obj.navigate_settings()

    def draw( self ):

        center = self.engine.screen_size.d( 2 )

        # Don't draw this if the user is viewing settings
        if ( not self._is_viewing_settings ):

            # Draw title icon
            self.engine.draw_sprite( 'title', V2(), center.c().s( 0, 170 ), True, anchor = V2( 0.5, 0.5 ) )

            # Draw the options
            self.engine.draw_text_bitmap( '[SPACE] Play', 'main', 3, center.c(), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[S] Settings', 'main', 3, center.c().a( 0, 60 ), True, anchor = V2( 0.5, 0.5 ) )

        # Draw settings menu if opened
        else:
            self._settings_obj.draw_settings()