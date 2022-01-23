from basic_imports import *

# Handles UI drawing & responses
class UIController():

    def __init__( self ):

        # State represents the UI menu
        self.__state = [ 1 ]

    def draw( self, engine ):

        if self.__state[0] == 1:
            engine.draw_text( '[ESC] Pause', 'main:20', V2( 20, 20 ), ( 255, 255, 255 ) )

            if engine.get_instance( 'controller' ).debug:
                engine.draw_text( 'Debug', 'main:12', engine.screen_size.c().s( 10, 10 ), ( 0, 100, 255 ), V2( 1, 1 ) )