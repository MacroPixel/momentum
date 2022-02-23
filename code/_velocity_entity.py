from basic_imports import *
from entity import *
from math import sin

class Velocity_Entity ( Entity ):

    def __init__( self, engine, object_id, pos, hitbox, sprite, modifier ):

        super().__init__( engine, object_id, pos, V2(), hitbox, layer = LAYER_ENTITY )

        self.__hover_time = 0
        self._cooldown = 0
        self._sprite = sprite
        self._modifier = modifier

    def update( self ):

        # Don't run if paused
        if ( self.engine.get_instance( 'controller' ).pause_level != PAUSE_NONE ):
            return

        # Call parent event
        super().update()

        # Add to hover time (controls hover animation)
        self.__hover_time += self.engine.delta_time * 1.5

        # Check if any entity should touch it
        # Break the loop if one is found to allow cooldown to start
        if self._cooldown <= 0:
            for entity in self.engine.get_tagged_instances( 'entity' ):

                # Rule out entities with no motion (including twig itself)
                if entity.vel == V2():
                    continue

                if utils.collision_check( self.pos.c(), entity.pos.c(), self.hitbox.c(), entity.hitbox.c(), self.hitbox_offset.c(), entity.hitbox_offset.c() ):
                    self.collide_effect( entity )
                    break

        # Countdown cooldown time (to prevent constantly resetting)
        self._cooldown -= self.engine.delta_time

    def draw( self ):

        hover_offset = sin( self.__hover_time ) / 4
        self.engine.draw_sprite( self._sprite, V2(), self.pos.c().a( 0, hover_offset ).m( GRID ), False )

    # Modifies velocity, starts cooldown, plays sound effect
    def collide_effect( self, entity ):

        self._cooldown = 1
        self.engine.get_instance( 'controller' ).shake_screen( 2, 0.3 )
        entity.vel.m( self._modifier )