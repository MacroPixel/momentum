from basic_imports import *
from entity import *

class Box_Long ( Entity ):

    def __init__( self, engine, pos ):

        # Boxes have a 2x2 block hitbox
        super().__init__( engine, 'box_long', pos, V2(), ( 4, 1, 0, 0 ) )

        # They can also be picked up/are solid
        self.entity_item = 'box_long'
        self.entity_dies_to_hazards = False
        self.add_tag( 'pickupable' )
        self.add_tag( 'solid_entity' )

    def update( self ):

        super().entity_update( iterations = 1 )

    # Shift the box upward when placed down
    def on_drop( self ):
        
        # Destroy if inside block
        if ( self.is_inside_block() is not None ):
            block_id = self.engine.get_instance( 'controller' ).get_block_type( self.is_inside_block() )
            if ( block_id not in B_PASSABLE ):
                self.delete()

    def draw( self ):

        self.engine.draw_sprite( 'box_long', V2(), self.pos.c().m( GRID ), False )