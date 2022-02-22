from basic_imports import *
from background import *
import random

# Background for the tutorial region
class Background_Region_4 ( Background ):

    def __init__( self, container ):

        self._bubble_positions = [ V2( random.randint( 15, 192 - 15 ), random.randint( 15, 192 - 15 ) ) for _ in range( 15 ) ]
        super().__init__( container )

    def update_surf( self, delta_time ):

        # Load surface into memory
        surf = self.engine.get_sprite( 'bg4_img0', V2( 0, random.randint( 0, 1 ) ) ).copy()

        # Then, draw the other stuff onto it
        fg_grass = self.engine.get_sprite( 'bg4_img1', V2( 0, random.randint( 0, 2 ) ) ).copy()
        surf.blit( fg_grass, ( 0, 0 ) )

        # Randomly draw bubbles
        fg_bubble = self.engine.get_sprite( 'bg4_img2', V2() ).copy()
        for bubble_pos in self._bubble_positions:
            bubble_pos.y -= random.randint( 0, 3 )
            if ( bubble_pos.y < 15 ):
                bubble_pos.y = 192 - 15
            surf.blit( fg_bubble, bubble_pos.l() )

        # Finally, scale it up 2x
        surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( 2 ).l() )
        self.__surf = surf

    def get_surf( self ):

        return self.__surf