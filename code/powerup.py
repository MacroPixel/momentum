from basic_imports import *
from entity import *
from math import sin

class Powerup ( Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'powerup', pos.c().a( 0, -0.5 ), V2(), ( 0.7, 0.7, 0.15, 0.15 ), layer = LAYER_BLOCK )

        # The ability this powerup grants depends on the block below it
        # It looks for the first block below it that isn't air
        # Uses ABILITY_BLOCKS, and throws error if value not found
        controller = self.engine.get_instance( 'controller' )
        for yy in range( floor( pos.y ), floor( pos.y ) + 10 ):
            if controller.is_block( V2( floor( self.pos.x ), yy ) ):
                ability_block = utils.b_string( controller.get_block_type( V2( floor( self.pos.x ), yy ) ) )
                break
        else:
            raise RuntimeError( 'No block found beneath powerup' )

        if ability_block in ABILITY_BLOCKS:
            self._ability_id = ABILITY_BLOCKS.index( ability_block )
        else:
            raise IndexError( f'{ ability_block } isn\'t defined as an ability block.' )

        # Destroy if player has ability
        if ( self.engine.get_instance( 'player' ).has_ability( ABILITY_STRINGS[ self.ability_id ] ) ):
            self.delete()

        self.__hover_time = 0
        self.__pulse_time = 0 # For background

        # Entity variables
        self.entity_gravity_multiplier = 0

    def update( self ):

        # Don't run if paused
        if ( self.engine.get_instance( 'controller' ).pause_level != PAUSE_NONE ):
            return

        # Call parent event
        super().entity_update()

        # Add to hover time (controls hover animation)
        # Also add to pulse time to control white background
        self.__hover_time += self.engine.delta_time * 1.5
        self.__pulse_time += self.engine.delta_time * 4

    def draw( self ):

        hover_offset = sin( self.__hover_time ) / 4
        pulse = round( sin( self.__pulse_time ) * 1.5 + 1.5 )
        self.engine.draw_sprite( 'powerup_bg', V2( 0, pulse ), self.pos.c().a( 0, hover_offset ).m( GRID ).s( 2 ), False )
        self.engine.draw_sprite( 'powerup', V2( 0, self.ability_id ), self.pos.c().a( 0, hover_offset ).m( GRID ), False )

    # Getters/setters

    @property
    def ability_id( self ):
        return self._ability_id