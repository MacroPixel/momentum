from basic_imports import *

class Menu_Controller ( Game_Object ):

    def __init__( self, engine ):

        # Nothing to store
        super().__init__( engine, 'menu_controller', layer = 1 )

        # This is when the game is first loaded, so fonts must be initialized
        engine.create_bitmap_font( '/textures/font_1.png', 'main', space_width = 6 )

    def update( self ):
        
        # Goto main room if button is pressed
        if ( self.engine.get_key( pygame.K_SPACE, 1 ) ):
            self.engine.load_room( 'main' )

        # Quit if escape is pressed
        if ( self.engine.get_key( pygame.K_ESCAPE, 1 ) ):
            self.engine.close_app()

    # Draw the "press space" text
    def draw( self ):

        self.engine.draw_text_bitmap( 'PRESS SPACE', 'main', 4, self.engine.screen_size.d( 2 ), True, anchor = V2( 0.5, 0.5 ) )
        self.engine.draw_text_bitmap( 'the quick brown fox jumps over the lazy dog', 'main', 2, self.engine.screen_size.d( 2 ).a( 0, 150 ), True, anchor = V2( 0.5, 0.5 ) )