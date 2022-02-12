from basic_imports import *

from _controller_level import *
from _controller_ui import *
from _controller_particle import *

from jomper import *

import random

# Controls basic game logic
# Other controller objects exist for more specific game logic
class Controller( Game_Object ):

    def __init__( self, engine ):

        # Initialize GameObject
        super().__init__( engine, 'controller', layer = LAYER_UI )

        # Pause level determines the amount of movement allowed
        self.pause_level = PAUSE_NONE

        # Initialize specialized sub-controllers
        self.__c_level = LevelController( self )
        self.__c_ui = UIController( self )
        self.__c_particle = ParticleController( self )

        # Death messages are loaded from res/data/death_strings.txt
        self.__death_strings = open( self.engine.get_path( '/data/death_strings.txt' ) ).read().split( '\n' )
        self._death_string_current = 'ERROR'

        # View stuff
        self._view_pos = V2()
        self.shake_reset()

        # Debug mode can be toggled with right alt
        self.__allow_debug = True
        self._debug = True
        self._advanced_info = False

    # Mostly just debug stuff
    def update( self ):

        # Toggle pause
        if self.engine.get_key( pygame.K_ESCAPE, 1 ):

            if self.pause_level == PAUSE_NONE:
                self.pause_level = PAUSE_NORMAL
            elif self.pause_level == PAUSE_NORMAL:
                self.pause_level = PAUSE_NONE

        # Switch debug mode if allowed
        if self.__allow_debug and self.engine.get_key( pygame.K_RALT, 1 ):
            self._debug = not self.debug

        # Quit the game is paused
        if ( self.engine.get_key( K_q, 1 ) and self.pause_level == PAUSE_NORMAL ):
            self.engine.load_room( 'frontend' )

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

            # Rewrite level
            if ( self.engine.get_key( pygame.K_F3, 1 ) ):
                self.__c_level.rewrite_level()

            # Reset level
            if ( self.engine.get_key( pygame.K_F4, 1 ) ):
                self.reset_level()

            # Object operation
            if ( self.engine.get_key( pygame.K_BACKQUOTE, 1 ) ):
                self.__c_level.object_debug()

            # Teleport to cursor
            if ( self.engine.get_mouse_button( 2, 1 ) ):
                self.engine.get_instance( 'player' ).pos = self.engine.get_world_cursor().d( GRID )
                self.engine.get_instance( 'player' ).vel = V2()

            # Misc operation 1
            if ( self.engine.get_key( pygame.K_F5, 1 ) ):
                Jomper( self.engine, self.engine.get_instance( 'player' ).pos.c().a( 0.5 ) )

            # Misc operation 2
            if ( self.engine.get_key( pygame.K_F6, 1 ) ):
                temp_player = self.engine.get_instance( 'player' )
                temp_player.is_invincible = not temp_player.is_invincible

            # Misc operation 3
            if ( self.engine.get_key( pygame.K_F7, 1 ) ):
                self.engine.play_music( 'mus_tutorial', volume = 0.4 )

            # Misc operation 4
            if ( self.engine.get_key( pygame.K_F8, 1 ) ):
                self.engine.get_instance( 'background_container' ).set_active( 'tutorial' )

        # Perform sub-class updates
        self.__c_level.update()
        self.__c_particle.update()

        # Do screen shake
        self.update_shake()

    # Reset the player
    def load_checkpoint( self ):

        self.engine.get_instance( 'player' ).load_checkpoint()

    def reset_level( self ):

        # Reload tiles
        self.__c_level.load_level()

        # Erase all entities (excluding player)
        for entity in [ e for e in self.engine.get_tagged_instances( 'entity' ) if e.object_id != 'player' ]:
            entity.delete()

        # Reset player
        self.load_checkpoint()

    # Check whether anything exists at a position
    def is_object( self, pos ):

        return self.__c_level.is_object( pos )

    # Check whether a block exists at a position
    def is_block( self, pos ):

        return self.__c_level.is_block( pos )

    # Check whether an entity exists at a position
    def is_entity( self, pos ):

        return self.__c_level.is_entity( pos )

    # Get the block type of a position
    # !!! WILL throw error if there isn't a block there
    def get_object_type( self, pos ):

        return self.__c_level.get_object_type( pos )

    # Check whether a non-passable block exists at a position
    def is_solid( self, pos ):

        return self.__c_level.is_block( pos ) and utils.b_string( utils.obj_id_to_block( self.__c_level.get_object_type( pos ) ) ) not in B_PASSABLE

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

        self._death_string_current = self.__death_strings[ random.randint( 0, len( self.__death_strings ) - 1 ) ]

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