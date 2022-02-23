from basic_imports import *
from enemy import *
import random

class Guart ( Enemy ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'guart', pos, V2(), ( 1, 2, 0, 0 ) )

        # Guart simply stands still, but looks at player
        self._is_facing_right = False

    def update( self ):

        # Cancel if game is paused
        if ( self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL ):
            return

        Entity.entity_update( self, iterations = 1 )

        self._is_facing_right = self.engine.get_instance( 'player' ).pos.x > self.pos.x

    def draw( self ):

        draw_pos = self.pos.c().m( GRID )
        self.engine.draw_sprite( 'guart', V2(), draw_pos, False, flip = V2( 1 if self._is_facing_right else -1, 1 ) )
        self.update_ragdoll( 'guart', self.pos.c(), self._is_facing_right, V2( 1, 1 ) )