from basic_imports import *
from enemy import *
from math import sin, cos, atan, pi
import random

class Flooter ( Enemy ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'flooter', pos, V2(), ( 0.8, 0.8, 0.1, 0.1 ) )

        # Controls movement direction
        self._move_speed = 3
        self._move_dir = random.uniform( 0, 2 * pi )

    def update( self ):

        # Cancel if game is paused
        if ( self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL ):
            return

        # Apply random rotation to movement direction
        rotate_amount = random.uniform( -pi, pi )
        self._move_dir += rotate_amount * self.engine.delta_time

        # Update velocity based on rotation
        self.vel = V2( cos( self.move_dir ), sin( self.move_dir ) ).m( self.move_speed )

        # Actually move
        Entity.entity_update( self, iterations = 1 )

    def draw( self ):

        draw_pos = self.pos.c().m( GRID )
        self.engine.draw_sprite( 'flooter', V2(), draw_pos, False, rotation = self._move_dir * 180 / pi )

        self.update_ragdoll( 'flooter', self.pos.c(), False, V2( 0.5, 0.5 ) )

    # Getters/setters

    @property
    def move_speed( self ):
        return self._move_speed

    @property
    def move_dir( self ):
        return self._move_dir