from basic_imports import *

# Handles UI drawing & responses
class UIController():

    def __init__( self ):

        # State represents the UI menu
        self.__state = [ 1 ]

    def draw( self, engine, controller ):

        if self.__state[0] == 1:
            engine.draw_text( '[ESC] Pause', 'main:20', V2( 20, 20 ), True )

            # Debug text
            if controller.debug:

                engine.draw_text( 'Debug', 'main:12', engine.screen_size.c().s( 10, 10 ), True, ( 0, 100, 255 ), anchor = V2( 1, 1 ) )

                # Advanced info
                if controller.advanced_info:

                  engine.draw_text( f'FPS: { floor( engine.fps_current ) }', 'main:12', engine.screen_size.c().m( 1, 0 ).a( -10, 10 ), True, anchor = V2( 1, 0 ) )