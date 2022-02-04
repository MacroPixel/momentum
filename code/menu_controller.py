from basic_imports import *

class Menu_Controller ( Game_Object ):

    def __init__( self, engine ):

        # Nothing to store
        super().__init__( engine, 'menu_controller', layer = 1 )

        # This is when the game is first loaded, so fonts must be initialized
        engine.create_font( '/misc/font_1.otf', 'main', 20 )
        engine.create_font( '/misc/font_1.otf', 'main', 12 )
        engine.create_font( '/misc/font_1.otf', 'main', 36 )
        engine.create_font( '/misc/font_1.otf', 'main', 50 )

    def update( self ):
        
        # Goto main room if button is pressed
        if ( self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.load_room( 'main' )

    # Draw the "press space" text
    def draw( self ):

        self.engine.draw_text( 'Press Space', 'main:36', self.engine.screen_size.d( 2 ), True, anchor = V2( 0.5, 0.5 ) )