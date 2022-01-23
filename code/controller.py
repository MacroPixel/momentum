from basic_imports import *

from controller_block import *
from controller_ui import *

# Controls basic game logic
# Other controller objects exist for more specific game logic
class Controller( Game_Object ):

    def __init__( self, engine ):

        # Initialize GameObject
        super().__init__( engine, 'controller' )

        # Initialize specialized sub-controllers
        self.__c_block = BlockController( self.engine.get_path( '/data/blocks.txt' ) )
        self.__c_ui = UIController()

        # Create fonts
        engine.create_font( '/misc/font_1.otf', 'main', 20 )
        engine.create_font( '/misc/font_1.otf', 'main', 12 )

        # Debug mode can be toggled with right alt
        self.__allow_debug = True
        self._debug = True

    # Mostly just debug stuff
    def update( self ):

        # Switch debug mode if allowed
        if self.__allow_debug and self.engine.get_key( pygame.K_RALT, 1 ):
            self._debug = not self.debug

        # Debug features
        if self.debug:
            
            # Restart
            if ( self.engine.get_key( pygame.K_RCTRL, 1 ) ):
                self.restart( self.get_instance( 'player' ) )

            # Rewrite level
            if ( self.engine.get_key( pygame.K_F7, 1 ) ):
                c_block.rewrite_level()

            # Reload level
            if ( self.engine.get_key( pygame.K_F8, 1 ) ):
                c_block.load_level()

            # Block operation
            if ( self.engine.get_key( pygame.K_BACKQUOTE, 1 ) ):
                c_block.block_debug( pygame.mouse.get_pos(), self.engine.view_pos )

    # Reset the player & reload blocks
    def restart( self, player ):

        player.pos = V2( 0, 0 )
        player.vel = V2( 0, 0 )

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

        self.__c_block.draw( self.engine )
        self.__c_ui.draw( self.engine )

    # Getters/setters
    @property
    def debug( self ):
        return self._debug