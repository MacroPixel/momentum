from basic_imports import *

class Checkpoint ( Game_Object ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'checkpoint', layer = LAYER_BLOCK )

        self.pos = pos
        self._is_active = False

    def draw( self ):

        self.engine.draw_sprite( 'checkpoint', V2( 0, 0 ), self.pos.c().m( GRID ), False )