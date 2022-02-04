from basic_imports import *
from enemy import *

class Jomper ( Enemy ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'jomper', layer = 1 )
        self.pos = pos
        self.vel = V2( 0, 0 )

    def update( self ):

        # Physics

        # Vertical movement (gravity only)
        self.vel.y += GRAVITY * self.engine.delta_time

        # Actually move
        utils.move_solid( self.pos, self.vel, V2( 1, 1 ), self.engine, iterations = 1 )

    def draw( self ):

        draw_pos = self.pos.c().m( GRID )
        self.engine.draw_sprite( 'jomper', V2( 0, 0 ), draw_pos, False )