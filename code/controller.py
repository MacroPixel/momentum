from basic_imports import *

from _controller_block import *
from _controller_ui import *

from enemy_jomper import *

# Controls basic game logic
# Other controller objects exist for more specific game logic
class Controller( Game_Object ):

    def __init__( self, engine ):

        # Initialize GameObject
        super().__init__( engine, 'controller', layer = 10 )

        # Pause level determines the amount of movement allowed
        self.pause_level = PAUSE_NONE

        # Initialize specialized sub-controllers
        self.__c_block = BlockController( self.engine.get_path( '/data/blocks.txt' ) )
        self.__c_ui = UIController()

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

        # Restart the game if player is dead
        if ( self.engine.get_key( K_SPACE, 1 ) and not self.engine.get_instance( 'player' ).is_alive ):
            self.restart()

        # Debug features
        if self.debug:
            
            # Restart
            if ( self.engine.get_key( pygame.K_RCTRL, 1 ) ):
                self.restart()

            # Rewrite level
            if ( self.engine.get_key( pygame.K_F7, 1 ) ):
                self.__c_block.rewrite_level( self )

            # Reload level
            if ( self.engine.get_key( pygame.K_F8, 1 ) ):
                self.__c_block.load_level( self.engine.get_path( '/data/blocks.txt' ) )

            # Block operation
            if ( self.engine.get_key( pygame.K_BACKQUOTE, 1 ) ):
                self.__c_block.block_debug( pygame.mouse.get_pos(), self.engine.view_pos )

            # Toggle advanced info
            if ( self.engine.get_key( pygame.K_F5, 1 ) ):
                self._advanced_info = not self.advanced_info

            # Misc operation
            if ( self.engine.get_key( pygame.K_F6, 1 ) ):
                Jomper( self.engine, self.engine.get_instance( 'player' ).pos.c() )

    # Reset the player & reload blocks
    def restart( self ):

        self.engine.get_instance( 'player' ).restart()

    # Check whether a block exists at a position
    def is_block( self, pos ):

        return self.__c_block.is_block( pos )

    # Get the block type of a position
    # !!! WILL throw error if there isn't a block there
    def get_block_type( self, pos ):

        return self.__c_block.get_block_type( pos )

    # Performs an operation on the block the player is hovering over
    def block_debug( self, cursor_pos, view ):

        self.__c_block.get_block_type( cursor_pos, view )

    # Draw blocks/UI
    def draw( self ):

        self.__c_block.draw( self.engine, self )
        self.__c_ui.draw( self.engine, self )

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