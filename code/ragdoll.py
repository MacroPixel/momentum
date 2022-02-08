from basic_imports import *
import random

# Created in place of an entity after it dies
# Shoots slightly upward, then falls off of the screen and self-destructs
class Ragdoll( Game_Object ):

    def __init__( self, engine, sprite_surf, pos, vel, anchor ):

        super().__init__( engine, 'ragdoll', layer = LAYER_RAGDOLL )

        # Movement variables
        self._pos = pos.c().a( anchor )

        # Keeps the velocity of parent object, but has a limit of 15
        self._vel = vel.c().fn( lambda a: min( abs( a ), 15 ) * ( -1 if a < 0 else 1 ) ).s( 0, 1 )

        # Rotation speed matches the direction of x-velocity
        # Its magnitude is proportional to max( abs( x_vel ), abs( y_vel ) )
        # It's measured in degrees/second
        self._rotation = 0
        self._rotation_speed = random.randrange( 45, 50 )
        self._rotation_speed *= max( abs( self.vel.x ) + 0.5, abs( self.vel.y ) + 0.5 ) * ( -1 if self.vel.x > 0 else 1 )
        self._anchor = anchor

        # Sprite of parent object
        self._sprite_surf = sprite_surf

    # Move based off velocity and rotation speed
    def update( self ):

        # Cancel if game is paused
        if ( self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL ):
            return

        # Gravity
        self.vel.y += GRAVITY * self.engine.delta_time

        # Move
        self.pos.a( self.vel.c().m( self.engine.delta_time ) )

        # Rotate
        self._rotation += self.rotation_speed * self.engine.delta_time

        # Destroy if out of view
        if ( self.pos.y * GRID > self.engine.view_bound_max.y + 100 ):
            self.delete()

    def draw( self ):

        self.engine.draw_surface( self.sprite_surf, self.pos.c().m( GRID ), False, rotation = self.rotation, anchor = V2( 0.5, 0.5 ) )

    # Getters/setters
    @property
    def pos( self ):
        return self._pos

    @property
    def vel( self ):
        return self._vel

    @property
    def rotation( self ):
        return self._rotation

    @property
    def rotation_speed( self ):
        return self._rotation_speed

    @property
    def sprite_surf( self ):
        return self._sprite_surf

    @property
    def anchor( self ):
        return self._anchor