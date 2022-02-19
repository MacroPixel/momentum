from basic_imports import *
from background import *
from random import uniform

# Background for the tutorial region
class Background_Region_7 ( Background ):

    def __init__( self, container ):

        super().__init__( container )

    def update_surf( self, delta_time ):

        # Load surface into memory, scaling it up 2x
        surf = self.engine.get_sprite( 'bg7_img0', V2( 0, 0 ) ).copy()

        # Finally, scale it up 2x
        surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( 2 ).l() )
        self.__surf = surf

    def get_surf( self ):

        return self.__surf