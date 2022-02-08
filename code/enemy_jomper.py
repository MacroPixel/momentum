from basic_imports import *
from enemy import *

class Jomper ( Enemy ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'jomper', pos, V2(), V2( 0.9, 0.5 ) )

    def update( self ):

        # Cancel if game is paused
        if ( self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL ):
            return

        # Actually move
        Entity.entity_update( self, iterations = 1 )

    def draw( self ):

        draw_pos = self.pos.c().a( 0.05, 0.25 ).m( GRID )
        self.engine.draw_sprite( 'jomper', V2( 0, 0 ), draw_pos, False )

        self.update_ragdoll( 'jomper', self.pos.c(), self.vel.x < 0, V2( 0.5, 0.65 ) )