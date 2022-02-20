from basic_imports import *

class Menu_Controller ( Game_Object ):

    def __init__( self, engine ):

        # Nothing to store
        super().__init__( engine, 'menu_controller', layer = 1 )

        # Play menu song
        self.engine.play_music( 'mus_menu_2', volume = 0.6 )

    def update( self ):
        
        # Goto main room if button is pressed
        if ( self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.switch_room( 'main' )

        # Quit if escape is pressed
        if ( self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self.engine.close_app()

    def draw( self ):

        center = self.engine.screen_size.d( 2 )

        # Draw title icon
        self.engine.draw_sprite( 'title', V2(), center.c().s( 0, 170 ), True, anchor = V2( 0.5, 0.5 ) )

        # Draw the options
        self.engine.draw_text_bitmap( '[SPACE] Play', 'main', 3, self.engine.screen_size.d( 2 ), True, anchor = V2( 0.5, 0.5 ) )