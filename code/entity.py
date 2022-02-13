from basic_imports import *
from ragdoll import *

class Entity( Game_Object ):

    def __init__( self, engine, object_id, pos, vel, hitbox_rect, layer = LAYER_ENTITY ):

        super().__init__( engine, object_id, layer = layer )
        self.add_tag( 'entity' )

        # Basic physics properties
        self.pos = pos
        self.vel = vel

        # Hitbox properties
        # Hitboxes are defined by (width, height, offset_x, offset_y)
        # Offset is measured relative to the top-left
        self._hitbox = V2( hitbox_rect[:2] )
        self._hitbox_offset = V2( hitbox_rect[2:4] )

        # Ragdoll physics
        # Ragdoll isn't created if either of the first two is None
        self.__ragdoll_sprite = None
        self.__ragdoll_pos = None
        self.__ragdoll_anchor = V2( 0.5, 0.5 )

        # Flags to allow customization
        self.entity_dies_to_spikes = True # Whether the entity can survive spikes
        self.entity_destroy_on_death = True # Whether the entity's GameObject is destroyed upon death
        self.entity_gravity_multiplier = 1 # Can be used to alter or disable gravity
        self.entity_item = None # Setting this to a string + adding 'pickupable' tag makes this pickupable

        # Other
        self.controller = self.engine.get_instance( 'controller' )

    # Moves based on position and velocity
    # Can also perform events common to all entities, such as death
    def entity_update( self, iterations = 5 ):

        # First, apply gravity
        self.vel.y += GRAVITY * self.engine.delta_time * self.entity_gravity_multiplier

        # The push functions aren't run until after the iteration is done
        # This prevents them from being executed more than once
        # These variables keep track of whether a push has occured along an axis
        # and which block it was
        x_push_block = y_push_block = None

        # Collision functions work the same way
        # Each block position that is touched is stored, and the collision
        # function is ran on each one
        collision_blocks = []

        # This loop actually moves the entity
        # Push/collision functions are executed afterwards
        for i in range( iterations ):

            # First, actually move the entity
            self.pos.x += self.vel.x * self.engine.delta_time / iterations
            temp_block = self._push_out( is_x_axis = True )
            if ( temp_block != None ):
                x_push_block = temp_block

            self.pos.y += self.vel.y * self.engine.delta_time / iterations
            temp_block = self._push_out( is_x_axis = False )
            if ( temp_block != None ):
                y_push_block = temp_block

            # Only add collision blocks after push-out is finished
            for block_pos in self._get_adjacent_blocks():
                if block_pos not in collision_blocks:
                    collision_blocks.append( block_pos )

        # Perform the aforementioned push functions
        for xy in 'xy': # Doing it this way reduces boilerplate code

            if eval( f'{xy}_push_block' ) is not None:

                block_id = eval( f'{xy}_push_block' )

                # Execute the custom push function
                exec( f'self.{xy}_push_func( block_id )' )
                
                # Cancel the velocity if it's a normal block
                block_string = utils.b_string( block_id )
                if ( block_string not in B_BOUNCE ):
                    exec( f'self.vel.{xy} = 0' )
                elif ( block_string in B_BOUNCE ):
                    exec( f'self.vel.{xy} *= -B_BOUNCE[ block_string ]' )

        # Perform the aforementioned collision functions
        has_died = False # Only allow 1 death
        for block_pos in collision_blocks:

            # Air does nothing
            if ( not self.controller.is_block( block_pos ) ):
                continue
            block_id = utils.obj_id_to_block( self.controller.get_object_type( block_pos ) )

            # Spikes kill you
            if ( not has_died and self.entity_dies_to_spikes and utils.b_string( block_id ) == 'spikes' ):
                self.die()
                has_died = True

            # Run the collision function for the selected block type
            self.collision_func( self.controller.get_object_type( block_pos ) )

    # Push an entity out of any adjacent blocks
    # Returns whether a push-out occured
    def _push_out( self, is_x_axis ):

        adjacent_blocks = self._get_adjacent_blocks()

        # For every grid space the position is inside of
        for block_pos in adjacent_blocks:

            # Skip if no block occupies this grid space
            if ( not self.controller.is_block( block_pos ) ):
                continue

            # Store the block type
            block_type = utils.obj_id_to_block( self.controller.get_object_type( block_pos ) )

            # Skip if a passable block occupies this grid space
            if ( utils.b_string( block_type ) in B_PASSABLE ):
                continue

            xy = 'x' if is_x_axis else 'y' # Reduce boilerplate code

            # Push out based on their position within the block
            # The is_x_axis argument determines the axis it's pushed along
            direction = -1 if eval( f'self.pos.{xy} < block_pos.{xy}' ) else 1
            exec( f'self.pos.{xy} = block_pos.{xy} + direction * ( self.hitbox.{xy} + self.hitbox_offset.{xy} )' )
            return block_type

        return None

    # Returns a list of the vectors of any block position the entity
    def _get_adjacent_blocks( self ):

        output = []

        bound_1 = self.pos.c().a( self.hitbox_offset ).a( COLLISION_EPSILON )
        bound_2 = self.pos.c().a( self.hitbox_offset ).a( self.hitbox ).s( COLLISION_EPSILON )

        # if ( self.object_id == 'player' ):
        #     print( bound_1, bound_2 )

        for xx in range( int( floor( bound_1.x ) ), int( ceil( bound_2.x ) ) ):
            for yy in range( int( floor( bound_1.y ) ), int( ceil( bound_2.y ) ) ):    
                output.append( V2( xx, yy ) )
        return output

    # Should be called after each draw event
    # Surf can either be a surface or a sprite name
    def update_ragdoll( self, surf, pos, flip = False, anchor = None ):

        if isinstance( surf, str ):
            surf = self.engine.get_sprite( surf, V2( 0, 0 ) ).copy()

        if flip:
            surf = pygame.transform.flip( surf, True, False )

        if ( anchor is not None ):
            self.__ragdoll_anchor = anchor

        self.__ragdoll_sprite = surf
        self.__ragdoll_pos = pos # Should represent the origin

    # Custom collision functions

    # Executes when the entity horizontally collides with a block
    # Accepts the block ID as an input
    def x_push_func( self, block_id ):
        pass

    # Same as before, but for vertical collisions
    def y_push_func( self, block_id ):
        pass

    # Executes for each block the player is inside of
    def collision_func( self, block_id ):
        pass

    # Executes when the entity dies
    # Can be overwritten by child class
    def die( self ):

        # Delete this instance unless told not to
        if ( self.entity_destroy_on_death ):
            self.delete()

        # Create a ragdoll unless told not to
        if ( self.__ragdoll_sprite is not None and self.__ragdoll_pos is not None ):
            Ragdoll( self.engine, self.__ragdoll_sprite, self.__ragdoll_pos, self.vel, self.__ragdoll_anchor )

    # Executes when an item from the inventory slot is turned into this entity
    def on_drop( self ):
        pass

    # Executes when an entity is stored as an item
    # Deletes the entity and returns its item string
    def pickup( self ):

        item_str = self.entity_item
        self.delete()
        return item_str

    # Getters/setters
    @property
    def pos( self ):
        return self._pos

    @property
    def vel( self ):
        return self._vel

    # Position & velocity can only be set to new vectors
    @pos.setter
    def pos( self, value ):
        self._pos = V2( value )

    @vel.setter
    def vel( self, value ):
        self._vel = V2( value )

    @property
    def hitbox( self ):
        return self._hitbox

    @property
    def hitbox_offset( self ):
        return self._hitbox_offset