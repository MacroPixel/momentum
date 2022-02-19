from basic_imports import *
from entity import *
import random

class Saw ( Entity ):

    def __init__( self, engine, pos ):

        saw_blocks = {
            'metal': 'gear', # solid
            'metal_alt': 'gear',
            'wood': 'sawblade'
        }

        super().__init__( engine, 'saw', pos.c(), V2(), ( 1.5, 1.5, 0.25, 0.25 ), layer = LAYER_BLOCK )
        self.add_tag( 'hazardous' )

        # The sprite depends on the block below the saw
        # It looks for the first block below it that isn't air
        # Uses saw_blocks, and throws error if value not found
        controller = self.engine.get_instance( 'controller' )
        for yy in range( floor( pos.y ), floor( pos.y ) + 15 ):
            if controller.is_block( V2( floor( self.pos.x ), yy ) ):
                saw_block = utils.b_string( controller.get_block_type( V2( floor( self.pos.x ), yy ) ) )
                if saw_block in saw_blocks:
                    break
        else:
            self.delete()

        self._sprite = saw_blocks[ saw_block ]

        # Store image rotation
        self._rotation = 0
        self._rotation_speed = random.uniform( 300, 800 )

    def update( self ):

        # Don't run if paused
        if ( self.engine.get_instance( 'controller' ).pause_level != PAUSE_NONE ):
            return

        # Rotate
        self._rotation += self._rotation_speed * self.engine.delta_time

    def draw( self ):

        # Draw rotated saw
        draw_pos = self.pos.c().a( 1, 1 ).m( GRID )
        self.engine.draw_sprite( self._sprite, V2(), draw_pos, False, rotation = self._rotation, anchor = V2( 0.5, 0.5 ) )