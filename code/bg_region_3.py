from basic_imports import *
from background import *
import random

# Background for the tutorial region
class Background_Region_3 ( Background ):

    def __init__( self, container ):

        super().__init__( container )

    def update_surf( self, delta_time ):

        # Load surface into memory, scaling it up 2x
        surf = self.engine.get_sprite( 'bg3_img0', V2( 0, 0 ) ).copy()

        # Then, draw the other stuff onto it
        fg_gears = self.engine.get_sprite( 'bg3_img1', V2( 0, random.randint( 0, 1 ) ) ).copy()
        surf.blit( fg_gears, ( 0, 0 ) )

        # Finally, scale it up 2x
        surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( 2 ).l() )
        self.__surf = surf

    def get_surf( self ):

        return self.__surf