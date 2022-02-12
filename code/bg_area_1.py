from basic_imports import *
from background import *
from random import uniform

# Background for the tutorial area
class Background_Area_1 ( Background ):

    def __init__( self, container ):

        super().__init__( container )

    def update_surf( self, delta_time ):

        # Load surface into memory, scaling it up 2x
        surf = self.engine.get_sprite( 'bg1_img0', V2( 0, 0 ) ).copy()

        # Then, draw the other stuff onto it
        fg_blocks = self.engine.get_sprite( 'bg1_img1', V2( 0, 0 ) ).copy()
        surf.blit( fg_blocks, ( 0 + uniform( 0, 0.6 ), surf.get_height() - fg_blocks.get_height() + uniform( 0, 0.6 ) ) )

        # Finally, scale it up 2x
        surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( 2 ).l() )
        self.__surf = surf

    def get_surf( self ):

        return self.__surf