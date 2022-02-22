from basic_imports import *

from _controller_level import *
from _controller_ui import *
from _controller_particle import *
from _controller_region import *

from jomper import *
from player import *
from drawer import *
from settings import *

import random

# Controls basic game logic
# Other controller objects exist for more specific game logic
class Controller( Game_Object ):

    def __init__( self, engine ):

        # Initialize GameObject
        super().__init__( engine, 'controller', layer = LAYER_UI )

        # Pause level determines the amount of movement allowed
        self.pause_level = PAUSE_NONE

        # Variables controlling visible UI
        self._ability_info = -1
        self.is_viewing_settings = False

        # Initialize specialized sub-controllers
        self.__c_level = LevelController( self )
        self.__c_ui = UIController( self )
        self.__c_particle = ParticleController( self )
        self.__c_region = RegionController( self )

        # The player can now be initialized
        Player( self.engine, V2( self.get_level_meta( 'player_spawn' ) ), self.get_level_meta( 'abilities' ) )

        # A new death string is chosen every time the player dies
        self._death_string_current = 'ERROR'

        # Hold the settings object
        self._settings_obj = SettingsController( self.engine )

        # View stuff
        self._view_pos = V2()
        self.shake_reset()

        # Cutscene variables are a function of time elapsed
        # Also requires drawer for drawing behind player
        self._cutscene_time = 0
        Drawer( self.engine, LAYER_FADEOUT, self.fade_draw )

        # Debug mode can be toggled with right alt
        self.__allow_debug = True
        self._debug = True
        self._advanced_info = False

    # Mostly just debug stuff
    def update( self ):

        # Toggle pause/ability/settings menu
        if self.engine.get_key( pygame.K_ESCAPE, 1 ):

            if self.pause_level == PAUSE_NONE:
                self.pause_level = PAUSE_NORMAL
            elif self.pause_level == PAUSE_NORMAL and self._ability_info == -1 and not self.is_viewing_settings:
                self.pause_level = PAUSE_NONE
            elif self.pause_level == PAUSE_NORMAL and self._ability_info != -1:
                self._ability_info = -1
            elif self.pause_level == PAUSE_NORMAL and self.is_viewing_settings:
                self.is_viewing_settings = False

        # Ability stuff
        player = self.engine.get_instance( 'player' )
        valid_abilities = [ ABILITY_STRINGS.index( a ) for a in ABILITY_STRINGS if player.has_ability( a ) ]

        # Open abilities menu
        if ( self.pause_level == PAUSE_NORMAL and self.engine.get_key( K_a, 1 ) and self.ability_info == -1 and len( valid_abilities ) > 0 ):
            self._ability_info = valid_abilities[0] # Start on the first valid ability instead of ability 0

        # Open settings menu
        if ( self.pause_level == PAUSE_NORMAL and self.engine.get_key( K_s, 1 ) and not self.is_viewing_settings ):
            self.is_viewing_settings = True

        # Cycle through abilities menu
        if ( ( self.engine.get_key( K_RIGHT, 1 ) or self.engine.get_key( K_LEFT, 1 ) ) and self.ability_info != -1 ):

            # Get the list of abilities the player has
            valid_abilities = [ ABILITY_STRINGS.index( a ) for a in ABILITY_STRINGS if player.has_ability( a ) ]

            # Only allow the user to cycle through valid abilities
            addend = 1 if self.engine.get_key( K_RIGHT, 1 ) else -1
            self._ability_info = ( valid_abilities[ ( valid_abilities.index( self._ability_info ) + addend ) % len( valid_abilities ) ] )

        # Cycle through settings menu
        if ( self.is_viewing_settings ):
            self._settings_obj.navigate_settings()

        # Switch debug mode if allowed
        if self.__allow_debug and self.engine.get_key( pygame.K_RALT, 1 ):
            self._debug = not self.debug

        # Quit the game is paused
        if ( self.engine.get_key( K_q, 1 ) and self.pause_level == PAUSE_NORMAL ):
            self.save_level_meta()
            self.engine.switch_room( 'menu' )

        # Restart the game if player is dead and game is unpaused
        if ( self.pause_level == PAUSE_NONE and self.engine.get_key( K_SPACE, 1 ) and not self.engine.get_instance( 'player' ).is_alive ):
            self.load_checkpoint()

        # Debug features
        if self.debug:
            
            # Return to checkpoint
            if ( self.engine.get_key( pygame.K_RCTRL, 1 ) ):
                self.load_checkpoint()

            # Toggle advanced info
            if ( self.engine.get_key( pygame.K_F2, 1 ) ):
                self._advanced_info = not self.advanced_info

            # Reset level
            if ( self.engine.get_key( pygame.K_F4, 1 ) ):
                self.reset_level()

            # Object operation
            if ( self.engine.get_key( pygame.K_BACKQUOTE, 1 ) ):
                self.__c_level.object_debug()

            # Misc operation 1
            if ( self.engine.get_key( pygame.K_F5, 1 ) ):
                Jomper( self.engine, self.engine.get_instance( 'player' ).pos.c().a( 0.5 ) )

            # Misc operation 2
            if ( self.engine.get_key( pygame.K_F6, 1 ) ):
                temp_player = self.engine.get_instance( 'player' )
                temp_player.is_invincible = not temp_player.is_invincible

            # Misc operation 3
            if ( self.engine.get_key( pygame.K_F7, 1 ) ):
                temp_player = self.engine.get_instance( 'player' )
                for ability in ABILITY_STRINGS:
                    if not temp_player.has_ability( ability ):
                        temp_player.grant_ability( ability )
                        break

            # Misc operation 4
            if ( self.engine.get_key( pygame.K_F8, 1 ) ):
                self.engine.reload_sprites()
                self.engine.reload_sounds()

        # Perform sub-class updates
        self.__c_level.update()
        self.__c_particle.update()
        self.__c_region.update()

        # Do screen shake
        self.update_shake()

        # Do trophy cutscene
        if ( self.pause_level == PAUSE_TROPHY ):

            self._cutscene_time += self.engine.delta_time

            if ( self._cutscene_time > 9 ):
                self.engine.switch_room( 'menu' )

    # Draws a fade out behind the player
    def fade_draw( self ):

        if ( self.pause_level != PAUSE_TROPHY ):
            return

        surf = pygame.Surface( self.engine.screen_size.l() )
        surf.fill( ( 0, 0, 0 ) )
        surf.set_alpha( utils.clamp( ( self._cutscene_time - 3.5 ) / 1.5, 0, 1 ) * 255 )
        self.engine.draw_surface( surf, V2(), True )

        if ( self._cutscene_time > 5 ):
            utils.draw_text_shadow( self.engine, 'VICTORY', 'main', 6, self.engine.screen_size.c().d( 2 ).s( 0, 150 ), True, ( 120, 0, 255 ), ( 40, 0, 120 ), anchor = V2( 0.5, 0.5 ) )

    # Reset the player
    def load_checkpoint( self ):

        self.engine.get_instance( 'player' ).load_checkpoint()

    def reset_level( self ):

        # Reload tiles
        self.__c_level.load_level( 'level_main' )

        # Erase all entities (excluding player)
        for entity in [ e for e in self.engine.get_tagged_instances( 'entity' ) if e.object_id != 'player' ]:
            entity.delete()

    # Get the metadata of the whole level
    def get_level_meta( self, key ):
        return self.__c_level.get_level_meta( key )

    # Set level metadata/immediately write to file
    def set_level_meta( self, key, value ):
        return self.__c_level.set_level_meta( key, value )

    # Rewrite data from memory into file
    def save_level_meta( self ):
        self.__c_level.save_level_meta()

    # Check whether anything exists at a position
    def is_object( self, pos ):
        return self.__c_level.is_object( pos )

    # Check whether a block exists at a position
    def is_block( self, pos ):
        return self.__c_level.is_block( pos )

    # Check whether an entity exists at a position
    def is_entity( self, pos ):
        return self.__c_level.is_entity( pos )

    # Get the object type of a position
    def get_object_type( self, pos ):
        return self.__c_level.get_object_type( pos )

    # Get the block type of a position
    def get_block_type( self, pos ):
        return self.__c_level.get_block_type( pos )

    # Get the entity type of a position
    def get_entity_type( self, pos ):
        return self.__c_level.get_entity_type( pos )

    # Check whether a non-passable block exists at a position
    def is_solid( self, pos ):

        return self.__c_level.is_block( pos ) and utils.b_string( self.__c_level.get_block_type( pos ) ) not in B_PASSABLE

    # Performs an operation on the block the player is hovering over
    def block_debug( self, cursor_pos, view ):

        pass

    # Controller isn't responsible for level/ui controller draw events
    # This is because the controller is assigned to a single layer, meaning
    # drawing everything from it alone wouldn't be very versatile
    # The level/ui controller instead create objects to run their
    # draw events for them
    def draw( self ):
        pass

    # Choose a new death message
    def new_death_string( self ):

        self._death_string_current = lang.DEATH_STRINGS[ random.randint( 0, len( lang.DEATH_STRINGS ) - 1 ) ]

    # Show a tooltip for abilities menu
    def show_ability_tooltip( self, seconds ):

        self.__c_ui.show_ability_tooltip( seconds )

    # Pause the game and start drawing win stuff
    def start_win_sequence( self ):

        # Freeze the game
        self.pause_level = PAUSE_TROPHY

        # Reset cutscene
        self._cutscene_time = 0

        # Play victory sound
        pygame.mixer.music.stop()
        self.engine.play_sound( 'victory' )

    # Screen-shake related functions
    from _controller_shake import shake_reset
    from _controller_shake import shake_screen
    from _controller_shake import update_shake

    # Getters/setters
    @property
    def debug( self ):
        return self._debug

    @property
    def advanced_info( self ):
        return self._advanced_info

    @property
    def pause_level( self ):
        return self._pause_level

    @pause_level.setter
    def pause_level( self, value ):

        if not isinstance( value, int ) or not ( 0 <= value < PAUSE_TOTAL ):
            raise ValueError( 'Invalid pause level' )
        self._pause_level = value

    @property
    def is_player_dead( self ):
        return self._is_player_dead

    @property
    def death_string( self ):
        return self._death_string_current

    @property
    def net_view_pos( self ):
        return self._view_pos.c().a( self._view_shake )

    @property
    def view_pos( self ):
        return self._view_pos.c()

    @view_pos.setter
    def view_pos( self, value ):
        self._view_pos = value
        self.engine.view_pos = self.net_view_pos

    @property
    def view_shake( self ):
        return self._view_shake.c()

    @view_shake.setter
    def view_shake( self, value ):
        self._view_shake = value
        self.engine.view_pos = self.net_view_pos

    @property
    def ability_info( self ):
        return self._ability_info