from basic_imports import *
from entity import *
from math import sin

class Checkpoint ( Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'checkpoint', pos.c().a( 0 ), V2( 0, 0 ), ( 0.7, 0.7, 0.35, 0.35 ), layer = LAYER_BLOCK )

        self._real_pos = pos
        self._is_active = False
        self.__hover_time = 0

    def update( self ):

        # Don't run if paused
        if ( self.engine.get_instance( 'controller' ).pause_level != PAUSE_NONE ):
            return

        # Call parent event
        super().update()

        # Add to hover time (controls hover animation)
        self.__hover_time += self.engine.delta_time * 1.5

    def draw( self ):

        hover_offset = sin( self.__hover_time ) / 4
        self.engine.draw_sprite( 'checkpoint', V2( 0, 0 ), self.pos.c().a( 0, hover_offset - 0.5 ).m( GRID ), False )

    # Getters/setters

    @property
    def real_pos( self ):
        return self._real_pos

    @property
    def is_active( self ):
        return self._is_active