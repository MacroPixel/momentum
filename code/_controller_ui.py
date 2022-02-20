from basic_imports import *
from drawer import *
import os, psutil

# Handles UI drawing & responses
class UIController():

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.engine = self.controller.engine

        # Shows a message over badges for a certain amount of time
        self._ability_tooltip_timer = -1

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.engine, LAYER_UI, self.draw )

    def draw( self ):

        # Shorthand variables
        player = self.engine.get_instance( 'player' )
        screen_size = self.engine.screen_size.c()

        # Tick down timers
        self._ability_tooltip_timer -= self.engine.delta_time

        # Normal level UI
        if ( self.controller.pause_level == PAUSE_NONE ):

            # Pause text
            self.engine.draw_text_bitmap( '[ESC] Pause', 'main', 2, V2( 15, 15 ), True )

            # Ability badges
            x_offset = 0
            for i, ability in enumerate( ABILITY_STRINGS ):
                if player.has_ability( ability ):

                    temp_pos = V2( 10 + x_offset * 20, screen_size.y - 10 )
                    self.engine.draw_sprite( 'badges', V2( 0, i ), temp_pos, True, scale = V2( 2, 2 ), anchor = V2( 0, 1 ) )
                    x_offset += 1

            # Ability tooltip
            if ( self._ability_tooltip_timer > 0 ):

                opacity = min( self._ability_tooltip_timer, 1 )
                self.engine.draw_text_bitmap( 'Press [ESC] to view abilities', 'main', 2, V2( 10, screen_size.y - 30 ), True, ( 255, 255, 255, opacity * 255 ), anchor = V2( 0, 1 ) )

            # Death text
            if ( not player.is_alive ):

                temp_pos = screen_size.c().d( 2 )
                temp_str = self.controller.death_string
                temp_colors = [ ( 255, 100, 100 ), ( 120, 0, 0 ) ]
                utils.draw_text_shadow( self.engine, temp_str, 'main', 4, temp_pos, True, color = temp_colors[0], shadow = temp_colors[1], anchor = V2( 0.5, 0.5 ) )

                death_count = f"Deaths: { self.controller.get_level_meta( 'deaths' ) }"
                temp_pos.a( 0, 70 )
                utils.draw_text_shadow( self.engine, death_count, 'main', 2, temp_pos, True, color = temp_colors[0], shadow = temp_colors[1], anchor = V2( 0.5, 0.5 ) )

            # Debug text
            if self.controller.debug:

                self.draw_debug_text()

        # Pause menu UI
        elif ( self.controller.pause_level == PAUSE_NORMAL and self.controller.ability_info == -1 ):

            self.engine.draw_text_bitmap( '[ESC] Resume', 'main', 2, V2( 15, 15 ), True )

            # Abilities are only shown if the player has one or more abilities
            has_abilities = len( [ 0 for ability in ABILITY_STRINGS if player.has_ability( ability ) ] ) > 0
            if has_abilities:
                self.engine.draw_text_bitmap( '[A] Abilities', 'main', 2, V2( 15, 40 ), True )
                self.engine.draw_text_bitmap( '[Q] Save and Quit', 'main', 2, V2( 15, 65 ), True )
            else:
                self.engine.draw_text_bitmap( '[Q] Save and Quit', 'main', 2, V2( 15, 40 ), True )

        # Ability info UI
        elif ( self.controller.ability_info != -1 ):

            # Draw black background
            temp_surf = pygame.Surface( self.engine.screen_size.l(), pygame.SRCALPHA, 32 )
            temp_surf.fill( ( 0, 0, 0, 200 ) )
            self.engine.draw_surface( temp_surf, V2(), True )

            # Draw controls
            self.engine.draw_text_bitmap( '[ESC] Back', 'main', 2, V2( 15, 15 ), True )
            self.engine.draw_text_bitmap( '[</>] Navigate', 'main', 2, V2( 15, 40 ), True )

            # Draw current ability text
            title_text = lang.ABILITY_INFO[ self.controller.ability_info ][0]
            title_color = ABILITY_COLORS[ self.controller.ability_info ]
            self.engine.draw_text_bitmap( title_text, 'main', 4, V2( self.engine.screen_size.x / 2, 120 ), True, utils.hex_to_rgb( title_color ), anchor = V2( 0.5, 0 ) )

            for i, line in enumerate( lang.ABILITY_INFO[ self.controller.ability_info ][1:] ):
                self.engine.draw_text_bitmap( line, 'main', 2, V2( self.engine.screen_size.x / 2, 200 + 25 * i ), True, anchor = V2( 0.5, 0 ) )

    # Reduces code clutter
    def draw_debug_text( self ):
        
        player = self.engine.get_instance( 'player' )

        corner_pos = self.engine.screen_size.c().m( 1, 0 ).a( -10, 10 )
        self.engine.draw_text_bitmap( 'DEBUG', 'main', 1, corner_pos.c().a( 0, 0 ), True, ( 0, 100, 255 ), anchor = V2( 1, 0 ) )

        # Advanced info
        if self.controller.advanced_info:

            draw_pos = corner_pos.c()

            fps_str = f"FPS: { floor( self.engine.fps_current ) }"
            self.engine.draw_text_bitmap( fps_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            position_str = f"Position: { player.pos.c().fn( lambda a: floor( a ) ) }"
            self.engine.draw_text_bitmap( position_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            velocity_str = f"Velocity: { player.vel.c().fn( lambda a: floor( a ) ) }"
            self.engine.draw_text_bitmap( velocity_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            chunk_str = f"Chunk: { player.pos.c().fn( lambda a: floor( a / C_GRID ) ) }"
            self.engine.draw_text_bitmap( chunk_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            c_loaded_str = f"Chunks Loaded: { len( self.controller._Controller__c_level._LevelController__loaded_chunks ) }"
            self.engine.draw_text_bitmap( c_loaded_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )
            memory_str = f"Memory Used: { round( psutil.Process( os.getpid() ).memory_info().rss / 1024 ** 2, 1 ) } MB"
            self.engine.draw_text_bitmap( memory_str, 'main', 1, draw_pos.a( 0, 15 ), True, anchor = V2( 1, 0 ) )

    # Enable ability tooltip for a certain amount of seconds
    def show_ability_tooltip( self, seconds ):

        self._ability_tooltip_timer = seconds

    @property
    def controller( self ):
        return self._controller