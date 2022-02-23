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

        self._is_resetting_data = False

    def update( self ):
        
        # Goto main room if button is pressed
        if ( not self._is_viewing_settings and not self._is_resetting_data and self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.switch_room( 'main' )

        # Quit if escape is pressed
        if ( not self._is_viewing_settings and not self._is_resetting_data and self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self.engine.close_app()

        # Go to/exit settings menu
        if ( not self._is_viewing_settings and not self._is_resetting_data and self.engine.get_key( pygame.K_s, 1 ) ):
            self._is_viewing_settings = True
        elif ( self._is_viewing_settings and self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self._is_viewing_settings = False

        # Go to/exit reset data screen
        if ( not self._is_viewing_settings and not self._is_resetting_data and self.engine.get_key( pygame.K_LCTRL ) and self.engine.get_key( pygame.K_r, 1 ) ):
            self._is_resetting_data = True
        elif ( self._is_resetting_data and self.engine.get_key( pygame.K_LSHIFT ) and self.engine.get_key( pygame.K_DELETE, 1 ) ):
            file = open( self.engine.get_path( '/data/level_main/level_meta.json' ), 'w' )
            file.close()
            self._is_resetting_data = False
        elif ( self._is_resetting_data and self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self._is_resetting_data = False

        # Cycle through settings menu
        if ( self._is_viewing_settings ):
            self._settings_obj.navigate_settings()

    def draw( self ):

        center = self.engine.screen_size.d( 2 )

        # Don't draw this if the user is viewing settings
        if ( not self._is_viewing_settings and not self._is_resetting_data ):

            # Draw the background
            bg_surf = pygame.Surface( self.engine.screen_size.l() )
            bg_surf.fill( ( 30, 30, 30 ) )
            self.engine.draw_surface( bg_surf, V2(), True )

            # Draw title icon
            self.engine.draw_sprite( 'title', V2(), center.c().s( 0, 170 ), True, anchor = V2( 0.5, 0.5 ) )

            # Draw the options
            self.engine.draw_text_bitmap( '[SPACE] Play', 'main', 3, center.c(), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[S] Settings', 'main', 3, center.c().a( 0, 60 ), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[CTRL+R] Reset Data', 'main', 3, center.c().a( 0, 120 ), True, color = ( 255, 120, 120 ), anchor = V2( 0.5, 0.5 ) )

            # Draw version
            self.engine.draw_text_bitmap( 'v1.0', 'main', 2, V2( 10, self.engine.screen_size.y - 10 ), True, anchor = V2( 0, 1 ) )

        # Draw settings menu if opened
        elif ( self._is_viewing_settings ):
            self._settings_obj.draw_settings()

        # Draw reset data screen
        elif ( self._is_resetting_data ):
            self.engine.draw_text_bitmap( 'Press SHIFT and DELETE to reset data.', 'main', 3, center.c(), True, color = ( 255, 120, 120 ), anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( 'This cannot be undone.', 'main', 3, center.c().a( 0, 70 ), True, color = ( 255, 20, 20 ), anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[ESC] Back', 'main', 2, V2( 15, 15 ), True )