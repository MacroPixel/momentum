from basic_imports import *
from entity import *
from math import atan, pi, sin, cos

class Rope_Hook ( Entity ):

    ROPE_LENGTH = 3

    def __init__( self, engine, pos ):

        super().__init__( engine, 'rope_hook', pos, V2(), ( 2, 2, -0.5, -0.5 ), LAYER_ENTITY )

        # Stores the player object if the player is hooked
        # Otherwise, holds None
        self._hooked_player = None

    def get_acceleration( self ):
        
        # This calculation is entirely based on the distance
        # between the hook and player
        player = self.engine.get_instance( 'player' )
        dist_magnitude = utils.dist( self.pos, self.engine.get_instance( 'player' ).pos )
        dist_angle = atan( ( self.pos.y - player.pos.y ) / ( self.pos.x - player.pos.x ) )
        if ( self.pos.x - player.pos.x ) < 0:
            dist_angle += pi

        # Acceleration doesn't apply if rope isn't taut
        if ( dist_magnitude < self.ROPE_LENGTH ):
            return V2()

        # If the rope is taut, acceleration is opposite to the distance vector
        # Its magnitude increases as a polynomial function as the rope stretches
        output_magnitude = ( ( dist_magnitude - self.ROPE_LENGTH ) ) * 10
        output_angle = dist_angle
        return V2( output_magnitude * cos( output_angle ), output_magnitude * sin( output_angle ) )

    def draw( self ):

        self.engine.draw_sprite( 'rope_hook', V2(), self.pos.c().m( GRID ), False )

    # Getters/setters

    @property
    def hooked_player( self ):
        return hooked_player