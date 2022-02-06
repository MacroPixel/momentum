from basic_imports import *

# Handles UI drawing & responses
class UIController():

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.__engine = self.controller.engine

    def draw( self ):

        # Normal level UI
        if ( self.controller.pause_level == PAUSE_NONE ):

            # Pause text
            self.__engine.draw_text( '[ESC] Pause', 'main:20', V2( 20, 20 ), True )

            # Death text
            if ( not self.__engine.get_instance( 'player' ).is_alive ):
                self.__engine.draw_text( 'You Died', 'main:50', self.__engine.screen_size.c().d( 2 ), True, ( 255, 100, 100 ), anchor = V2( 0.5, 0.5 ) )

            # Debug text
            if self.controller.debug:

                self.__engine.draw_text( 'Debug', 'main:12', self.__engine.screen_size.c().s( 10, 10 ), True, ( 0, 100, 255 ), anchor = V2( 1, 1 ) )

                # Advanced info
                if self.controller.advanced_info:
                  self.__engine.draw_text( f'FPS: { floor( self.__engine.fps_current ) }', 'main:12', self.__engine.screen_size.c().m( 1, 0 ).a( -10, 10 ), True, anchor = V2( 1, 0 ) )

        # Pause menu UI
        elif ( self.controller.pause_level == PAUSE_NORMAL ):

            # Resume text
            self.__engine.draw_text( '[ESC] Resume', 'main:20', V2( 20, 20 ), True )

            # Quit text
            self.__engine.draw_text( '[Q] Quit', 'main:20', V2( 20, 50 ), True )

    @property
    def controller( self ):
        return self._controller