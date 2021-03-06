from basic_imports import *

class Frontend_Controller ( Game_Object ):

    def __init__( self, engine ):

        # Nothing to store
        super().__init__( engine, 'frontend_controller', layer = 1 )

    def update( self ):
        
        # Goto main room if button is pressed
        if ( self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.switch_room( 'main' )

        # Quit if escape is pressed
        if ( self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self.engine.close_app()

    def draw( self ):

        # Draw the "press space" text
        self.engine.draw_text_bitmap( 'PRESS SPACE', 'main', 4, self.engine.screen_size.d( 2 ), True, anchor = V2( 0.5, 0.5 ) )