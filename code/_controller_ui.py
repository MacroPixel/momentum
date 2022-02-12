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

        # Shorthand variables
        player = self.__engine.get_instance( 'player' )
        screen_size = self.__engine.screen_size.c()

        # Normal level UI
        if ( self.controller.pause_level == PAUSE_NONE ):

            # Pause text
            self.__engine.draw_text_bitmap( '[ESC] Pause', 'main', 2, V2( 15, 15 ), True )

            # Ability badges
            x_offset = 0
            for i, ability in enumerate( ABILITY_STRINGS ):
                if player.has_ability( ability ):
                    self.__engine.draw_sprite( 'badges', V2( 0, i ), V2( 10 + x_offset * 20, screen_size.y - 10 ), True, scale = V2( 2, 2 ), anchor = V2( 0, 1 ) )
                    x_offset += 1

            # Death text
            if ( not player.is_alive ):
                self.__engine.draw_text_bitmap( self.controller.death_string, 'main', 4, screen_size.c().d( 2 ).s( 4 ), True, ( 120, 0, 0 ), anchor = V2( 0.5, 0.5 ) )
                self.__engine.draw_text_bitmap( self.controller.death_string, 'main', 4, screen_size.c().d( 2 ), True, ( 255, 100, 100 ), anchor = V2( 0.5, 0.5 ) )

            # Debug text
            if self.controller.debug:

                self.draw_debug_text()

        # Pause menu UI
        elif ( self.controller.pause_level == PAUSE_NORMAL ):

            self.__engine.draw_text_bitmap( '[ESC] Resume', 'main', 2, V2( 15, 15 ), True )

            # Abilities are only shown if the player has one or more abilities
            has_abilities = len( [ 0 for ability in ABILITY_STRINGS if player.has_ability( ability ) ] ) > 0
            if has_abilities:
                self.__engine.draw_text_bitmap( '[A] Abilities', 'main', 2, V2( 15, 40 ), True )
                self.__engine.draw_text_bitmap( '[Q] Quit', 'main', 2, V2( 15, 65 ), True )
            else:
                self.__engine.draw_text_bitmap( '[Q] Quit', 'main', 2, V2( 15, 40 ), True )

    # Reduces code clutter
    def draw_debug_text( self ):
        
        player = self.__engine.get_instance( 'player' )

        corner_pos = self.__engine.screen_size.c().m( 1, 0 ).a( -10, 10 )
        self.__engine.draw_text_bitmap( 'DEBUG', 'main', 1, corner_pos.c().a( 0, 0 ), True, ( 0, 100, 255 ), anchor = V2( 1, 0 ) )

        # Advanced info
        if self.controller.advanced_info:

            draw_pos = corner_pos.c()

            fps_str = f"FPS: { floor( self.__engine.fps_current ) }"
            self.__engine.draw_text_bitmap( fps_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            position_str = f"Position: { player.pos.c().fn( lambda a: floor( a ) ) }"
            self.__engine.draw_text_bitmap( position_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            chunk_str = f"Chunk: { player.pos.c().fn( lambda a: floor( a / C_GRID ) ) }"
            self.__engine.draw_text_bitmap( chunk_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            velocity_str = f"Velocity: { player.vel.c().fn( lambda a: floor( a ) ) }"
            self.__engine.draw_text_bitmap( velocity_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            c_loaded_str = f"Chunks Loaded: { len( self.controller._Controller__c_level._LevelController__loaded_chunks ) }"
            self.__engine.draw_text_bitmap( c_loaded_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            r_loaded_str = f"Regions Loaded: { len( self.controller._Controller__c_level._LevelController__loaded_regions ) }"
            self.__engine.draw_text_bitmap( r_loaded_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )

    @property
    def controller( self ):
        return self._controller