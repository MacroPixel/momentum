from basic_imports import *
from enemy import *
from math import sin, cos, atan, pi
import random

class Jomper ( Enemy ):

    CHARGE_INTERVAL = ( 3, 5 )

    def __init__( self, engine, pos ):

        super().__init__( engine, 'jomper', pos, V2(), ( 0.8, 0.5, 0.1, 0.5 ) )

        # Controls how the jomper moves
        self._charge_timer = random.uniform( *self.CHARGE_INTERVAL )
        self.is_facing_right = True

    def update( self ):

        # Cancel if game is paused
        if ( self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL ):
            return

        # Tick down the charge timer
        self._charge_timer -= self.engine.delta_time

        # If timer is done, check if it can track player
        if ( self.charge_timer <= 0 ):

            # Reset the timer
            self._charge_timer = random.uniform( *self.CHARGE_INTERVAL )

            # The player must be within a 16 x 16 grid
            player = self.engine.get_instance( 'player' )
            if utils.collision_check( player.pos.c(), self.pos.c(), player.hitbox.c(), V2( 16, 16 ), player.hitbox_offset.c(), V2( -8, -8 ) ):
                
                # Jump towards player
                angle = atan( ( player.pos.y - self.pos.y ) / ( player.pos.x - self.pos.x ) )
                if ( player.pos.x - self.pos.x ) < 0:
                    angle += pi
                self.vel = V2( cos( angle ), sin( angle ) ).m( 15 ).a( 0, -5 )
                self.is_facing_right = self.vel.x > 0

        # Apply friction to velocity
        self.vel.x = max( abs( self.vel.x ) - 10 * self.engine.delta_time, 0 ) * utils.sign( self.vel.x )

        # Actually move
        Entity.entity_update( self, iterations = 1 )

    def draw( self ):

        draw_pos = self.pos.c().m( GRID )
        image_pos = 1 if self.charge_timer < 0.4 else 0
        self.engine.draw_sprite( 'jomper', V2( 0, image_pos ), draw_pos, False, flip = V2( 1 if self.is_facing_right else -1, 1 ) )

        ragdoll_surf = self.engine.get_sprite( 'jomper', V2( 0, image_pos ) ).copy()
        self.update_ragdoll( ragdoll_surf, self.pos.c(), self.is_facing_right, V2( 0.5, 0.65 ) )

    # Getters/setters

    @property
    def charge_timer( self ):
        return self._charge_timer