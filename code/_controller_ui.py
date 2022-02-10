from basic_imports import *
from drawer import *

# Handles UI drawing & responses
class UIController():

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.__engine = self.controller.engine

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.__engine, LAYER_UI, self.draw )

    def draw( self ):

        # Normal level UI
        if ( self.controller.pause_level == PAUSE_NONE ):

            # Pause text
            self.__engine.draw_text_bitmap( '[ESC] Pause', 'main', 2, V2( 15, 15 ), True )

            # Ability badges
            x_offset = 0
            for i, ability in enumerate( ABILITY_STRINGS ):
                if self.__engine.get_instance( 'player' ).has_ability( ability ):
                    self.__engine.draw_sprite( 'badges', V2( 0, i ), V2( 10 + x_offset * 20, self.__engine.screen_size.y - 10 ), True, scale = V2( 2, 2 ), anchor = V2( 0, 1 ) )
                    x_offset += 1

            # Death text
            if ( not self.__engine.get_instance( 'player' ).is_alive ):
                self.__engine.draw_text_bitmap( self.controller.death_string, 'main', 4, self.__engine.screen_size.c().d( 2 ).s( 4 ), True, ( 120, 0, 0 ), anchor = V2( 0.5, 0.5 ) )
                self.__engine.draw_text_bitmap( self.controller.death_string, 'main', 4, self.__engine.screen_size.c().d( 2 ), True, ( 255, 100, 100 ), anchor = V2( 0.5, 0.5 ) )

            # Debug text
            if self.controller.debug:

                corner_pos = self.__engine.screen_size.c().m( 1, 0 ).a( -10, 10 )
                self.__engine.draw_text_bitmap( 'DEBUG', 'main', 1, corner_pos.c().a( 0, 0 ), True, ( 0, 100, 255 ), anchor = V2( 1, 0 ) )

                # Advanced info
                if self.controller.advanced_info:
                  self.__engine.draw_text_bitmap( f'FPS: { floor( self.__engine.fps_current ) }', 'main', 1, corner_pos.c().a( 0, 15 ), True, anchor = V2( 1, 0 ) )

        # Pause menu UI
        elif ( self.controller.pause_level == PAUSE_NORMAL ):

            # Resume text
            self.__engine.draw_text_bitmap( '[ESC] Resume', 'main', 2, V2( 15, 15 ), True )

            # Quit text
            self.__engine.draw_text_bitmap( '[Q] Quit', 'main', 2, V2( 15, 40 ), True )

    @property
    def controller( self ):
        return self._controller