from basic_imports import *
from entity import *

class Trophy ( Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'trophy', pos, V2(), ( 1, 1, 0, 0 ), LAYER_TROPHY )
        self.entity_gravity_multiplier = 0

        self._current_image = 0
        self._current_alpha = 1
        self._cutscene_timer = 0

    def update( self ):

         # Perform image/entity update
        self._current_image += 24 * self.engine.delta_time
        super().entity_update( iterations = 1 )

        # Lerp towards player if during cutscene
        if ( self.engine.get_instance( 'controller' ).pause_level == PAUSE_TROPHY ):

            self._cutscene_timer += self.engine.delta_time

            # Lerp towards player
            player = self.engine.get_instance( 'player' )
            self.pos.x = utils.lerp( self.pos.x, player.pos.x, 0.8, self.engine.delta_time )
            self.pos.y = utils.lerp( self.pos.y, player.pos.y, 0.8, self.engine.delta_time )

            # Fade out
            # Occurs between t = 3 and t = 5
            self._current_alpha = utils.clamp( ( 3 - self._cutscene_timer ), 0, 1 )

            if self._current_alpha <= 0:
                self.delete()

    def draw( self ):

        if ( self._current_alpha == 1 ):
            self.engine.draw_sprite( 'trophy', V2( 0, floor( self._current_image ) % 60 ), self.pos.c().m( GRID ), False, scale = ( 0.33, 0.33 ) )
        else:
            surf = self.engine.get_sprite( 'trophy',  V2( 0, floor( self._current_image ) % 60 ) ).copy()
            surf.set_alpha( utils.clamp( self._current_alpha, 0, 1 ) * 255 )
            self.engine.draw_surface( surf, self.pos.c().m( GRID ), False, scale = ( 0.33, 0.33 ) )