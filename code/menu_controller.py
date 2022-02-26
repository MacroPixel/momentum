from basic_imports import *
from settings import *

class Menu_Controller ( Game_Object ):

    def __init__( self, engine ):

        super().__init__( engine, 'menu_controller', layer = 1 )

        # Play menu song
        self.engine.play_music( 'mus_menu_2' )

        # Load settings into memory
        self._settings_obj = SettingsController( self.engine )

        # Controls what the player is currently looking at
        self._view_mode = 'none'

    def update( self ):
        
        # Goto main room if button is pressed
        if ( self._view_mode == 'none' and self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.switch_room( 'main' )

        # Quit if escape is pressed, otherwise exit current menu
        if ( self.engine.get_key( pygame.K_ESCAPE, 1 ) ):

            if ( self._view_mode == 'none' ):
                self.engine.close_app()
            else:
                self._view_mode = 'none'

        # Go to different menus settings menu
        if ( self._view_mode == 'none' ):

            if ( self.engine.get_key( pygame.K_s, 1 ) ):
                self._view_mode = 'settings'
            elif ( self.engine.get_key( pygame.K_LCTRL ) and self.engine.get_key( pygame.K_r, 1 ) ):
                self._view_mode = 'reset'
            elif ( self.engine.get_key( pygame.K_k, 1 ) ):
                self._view_mode = 'keybinds'
            elif ( self.engine.get_key( pygame.K_c, 1 ) ):
                self._view_mode = 'credits'

        # Reset data screen
        elif ( self._view_mode == 'reset' and self.engine.get_key( pygame.K_LSHIFT ) and self.engine.get_key( pygame.K_DELETE, 1 ) ):
            file = open( self.engine.get_path( '/data/level_main/level_meta.json' ), 'w' )
            file.close()
            self._view_mode = 'none'

        # Cycle through settings menu
        if ( self._view_mode == 'settings' ):
            self._settings_obj.navigate_settings()

    def draw( self ):

        center = self.engine.screen_size.d( 2 )

        # Don't draw this if the user is viewing settings
        if ( self._view_mode == 'none' ):

            # Draw the background
            bg_surf = pygame.Surface( self.engine.screen_size.l() )
            bg_surf.fill( ( 30, 30, 30 ) )
            self.engine.draw_surface( bg_surf, V2(), True )

            # Draw title icon
            self.engine.draw_sprite( 'title', V2(), center.c().s( 0, 170 ), True, anchor = V2( 0.5, 0.5 ) )

            # Draw the options
            self.engine.draw_text_bitmap( '[SPACE] Play', 'main', 3, center.c().a( 0, -60 ), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[S] Settings', 'main', 3, center.c().a( 0, 0 ), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[K] View Keybinds', 'main', 3, center.c().a( 0, 60 ), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[C] Credits', 'main', 3, center.c().a( 0, 120 ), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[CTRL+R] Reset Data', 'main', 3, center.c().a( 0, 180 ), True, color = ( 255, 120, 120 ), anchor = V2( 0.5, 0.5 ) )

            # Draw version
            self.engine.draw_text_bitmap( 'v1.0.1', 'main', 2, V2( 10, self.engine.screen_size.y - 10 ), True, anchor = V2( 0, 1 ) )

        # Draw settings menu if opened
        elif ( self._view_mode == 'settings' ):
            self._settings_obj.draw_settings()

        # Draw reset data screen
        elif ( self._view_mode == 'reset' ):
            self.engine.draw_text_bitmap( 'Press SHIFT and DELETE to reset data.', 'main', 3, center.c(), True, color = ( 255, 120, 120 ), anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( 'This cannot be undone.', 'main', 3, center.c().a( 0, 70 ), True, color = ( 255, 20, 20 ), anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( '[ESC] Back', 'main', 2, V2( 15, 15 ), True )

        # Draw keybind info
        elif ( self._view_mode == 'keybinds' ):

            # Draw current ability text
            for i, line in enumerate( lang.KEYBIND_INFO ):
                self.engine.draw_text_bitmap( line, 'main', 2, V2( self.engine.screen_size.x / 2, 200 + 25 * i ), True, anchor = V2( 0.5, 0 ) )

        # Draw keybinds
        elif ( self._view_mode == 'keybinds' ):

            # Draw current ability text
            for i, line in enumerate( lang.KEYBIND_INFO ):
                self.engine.draw_text_bitmap( line, 'main', 2, V2( self.engine.screen_size.x / 2, 200 + 25 * i ), True, anchor = V2( 0.5, 0 ) )

        # Draw credits
        elif ( self._view_mode == 'credits' ):

            self.engine.draw_text_bitmap( 'MacroPixel: Programming, art, SFX', 'main', 2, self.engine.screen_size.d( 2 ).a( 0, -25 ), True, anchor = V2( 0.5, 0.5 ) )
            self.engine.draw_text_bitmap( 'Caiden: Music', 'main', 2, self.engine.screen_size.d( 2 ).a( 0, 25 ), True, anchor = V2( 0.5, 0.5 ) )