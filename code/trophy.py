from basic_imports import *
from entity import *

class Trophy ( Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'trophy', pos, V2(), ( 1, 1, 0, 0 ) )
        self.entity_gravity_multiplier = 0

        self._current_image = 0

    def update( self ):

        self._current_image += 24 * self.engine.delta_time

        super().entity_update( iterations = 1 )

    def draw( self ):

        self.engine.draw_sprite( 'trophy', V2( 0, floor( self._current_image ) % 60 ), self.pos.c().m( GRID ), False, scale = ( 0.33, 0.33 ) )