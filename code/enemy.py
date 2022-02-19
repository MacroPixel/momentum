from basic_imports import *
from entity import *

class Enemy ( Entity ):
    
    def __init__( self, engine, name, pos, vel, hitbox ):

        super().__init__( engine, name, pos, vel, hitbox )

        # Tags allow quick indexing of all enemies
        self.add_tag( 'enemy' )
        self.add_tag( 'hazardous' )

    # Play sound when killed
    def die( self ):

        self.engine.play_sound( 'enemy_death' )
        super().die()