from basic_imports import *
from entity import *

class Bomb ( Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'bomb', pos, V2(), ( 1, 1, 0, 0 ) )

        # Bombs can be picked up
        # By default, their fuse is deactivated
        self._fuse = None
        self.entity_dies_to_hazards = False
        self.entity_item = 'bomb'
        self.add_tag( 'pickupable' )

    def update( self ):

        super().entity_update( iterations = 1 )

        # Tick down fuse if necessary
        if ( self._fuse is not None ):

            self._fuse -= self.engine.delta_time

            # Explode if fuse is out
            if ( self._fuse < 0 ):
                self.explode()

    # Shift the box upward when placed down
    def on_drop( self ):

        # Start fuse (3 seconds)
        self._fuse = 3

    def explode( self ):

        # Kill any nearby enemies
        for entity in self.engine.get_tagged_instances( 'entity' ):
            if entity.entity_dies_to_hazards:
                if utils.collision_check( self.pos.c(), entity.pos.c(), V2( 10, 10 ), entity.hitbox, V2( -4.5, -4.5 ), entity.hitbox_offset ):
                    entity.die()

        # Destroy effect
        for i in range( 25 ):
            self.engine.get_instance( 'controller' )._Controller__c_particle.create_simple(
                self.pos.c().a( 0.5 ), ( 2, 6 ), ( 0, 360 ), ( 1, 2 ), [ ( 50, 50, 50 ), ( 20, 20, 20 ) ], ( 0.4, 0.9 ), ( 1.5, 2 ) )
        self.engine.get_instance( 'controller' ).shake_screen( 5, 0.3 )
        self.engine.play_sound( 'explode' )
        self.delete()

    def draw( self ):

        image_x = 0
        if ( self._fuse is not None ):
            image_x = int( divmod( self._fuse, 0.09 )[1] / 0.03 ) + 1

        self.engine.draw_sprite( 'bomb', V2( 0, image_x ), self.pos.c().m( GRID ), False )