from basic_imports import *
from background import *

# Background for the tutorial area
class Background_Area_1 ( Background ):

    def __init__( self, engine ):

        super().init( self, engine )

        # Load surface into memory
        self.surf = self.engine.get_sprite( 'bg_a1_l2' ).copy()

    def update( self ):

        if not self.is_update_interval():
            return

    def draw( self ):

        self.update_pos( V2( self.surf.get_size() ) )
        self.engine.draw_surface( self.surf, self.pos, False )