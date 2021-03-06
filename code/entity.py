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
        self.entity_dies_to_hazards = True # Whether the entity can survive hazards
        self.entity_destroy_on_death = True # Whether the entity's GameObject is destroyed upon death
        self.entity_gravity_multiplier = 1 # Can be used to alter or disable gravity
        self.entity_item = None # Setting this to a string + adding 'pickupable' tag makes this pickupable

        # Other
        self.controller = self.engine.get_instance( 'controller' )

    # Moves based on position and velocity
    # Can also perform events common to all entities, such as death
    def entity_update( self, iterations = 5 ):

        # First, apply gravity to velocity
        self.vel.y += GRAVITY * self.engine.delta_time * self.entity_gravity_multiplier

        # Then, move the object
        # Velocity caps out at ENTITY_MAX_VEL
        self.vel.fn( lambda a: min( abs( a ), ENTITY_MAX_VEL ) * utils.sign( a ) )
        self.shift_pos( self.vel.c().m( self.engine.delta_time ), iterations, self.x_push_func, self.y_push_func, self.collision_func )

    # Shift the entity a certain distance, keeping their collision details in mind
    def shift_pos( self, delta_pos, iterations = 5, x_push_func = None, y_push_func = None, collision_func = None ):

        # The push functions aren't run until after the iteration is done
        # This prevents them from being executed more than once
        # These variables keep track of whether a push has occured along an axis
        # and which block it was
        x_push_pos = y_push_pos = None

        # Collision functions work the same way
        # Each block position that is touched is stored, and the collision
        # function is ran on each one
        collision_positions = []

        # This loop actually moves the entity
        # Push/collision functions are executed afterwards
        for i in range( iterations ):

            # First, actually move the entity
            self.pos.x += delta_pos.x / iterations
            temp_pos = self._push_out( is_x_axis = True )
            if ( temp_pos is not None ):
                x_push_pos = temp_pos

            self.pos.y += delta_pos.y / iterations
            temp_pos = self._push_out( is_x_axis = False )
            if ( temp_pos is not None ):
                y_push_pos = temp_pos

            # Only add collision blocks after push-out is finished
            for block_pos in self.get_adjacent_blocks():
                if block_pos not in collision_positions:
                    collision_positions.append( block_pos )

        # Perform the aforementioned push functions
        for xy in 'xy': # Doing it this way reduces boilerplate code

            push_result = eval( f'{xy}_push_pos' )

            if push_result is not None:

                # Cancel velocity if it's an entity
                if ( push_result == -1 ):
                    exec( f'self.vel.{xy} = 0' )

                # Do other stuff for blocks
                else:

                    block_pos = eval( f'{xy}_push_pos' )
                    block_id = self.controller.get_block_type( block_pos )

                    # Execute the custom push function
                    # Skips defaults if returns False
                    if ( eval( f'{xy}_push_func' ) is not None ):
                        exec( f'self.{xy}_push_func( block_id )' )
                    
                    # Cancel the velocity if it's a normal block
                    block_string = utils.b_string( block_id )
                    if ( abs( eval( f'self.vel.{xy}' ) ) < 0.0001 ):
                        exec( f'self.vel.{xy} = 0' )
                    if ( block_string not in B_BOUNCE ):
                        exec( f'self.vel.{xy} = 0' )
                    elif ( block_string in B_BOUNCE ):
                        exec( f'self.vel.{xy} *= -B_BOUNCE[ block_string ]' )
                        if ( abs( eval( f'self.vel.{xy}' ) ) > 1.2 ):
                            self.engine.play_sound( 'bounce' )

        # Perform the aforementioned collision functions
        has_died = False # Only allow 1 death
        for block_pos in collision_positions:

            # Run the collision function for the selected block type
            if ( collision_func is not None ):
                self.collision_func( block_pos )

            # Air does nothing
            if ( not self.controller.is_block( block_pos ) ):
                continue
            block_id = self.controller.get_block_type( block_pos )

            # Hazards kill you
            if ( not has_died and self.entity_dies_to_hazards and utils.b_string( block_id ) in B_HAZARD ):
                self.die()
                has_died = True

    # Returns the entity the player is inside of
    # Only works on entities with 'solid_entity' tag
    def is_inside_entity( self ):

        for entity in [ i for i in self.engine.get_tagged_instances( 'solid_entity' ) if i is not self ]:
            if utils.collision_check( *utils.collision_vars( self, entity ) ):
                return entity
        return None

    # Returns the block position the player is inside of, or none if in air/passable block
    # Also returns the block position
    def is_inside_block( self ):

        adjacent_blocks = self.get_adjacent_blocks()

        # For every grid space the position is inside of
        for block_pos in adjacent_blocks:

            # Skip if no block occupies this grid space
            if ( not self.controller.is_block( block_pos ) ):
                continue

            # Store the block type
            block_id = self.controller.get_block_type( block_pos )

            # Skip if a passable block occupies this grid space
            if ( utils.b_string( block_id ) in B_PASSABLE ):
                continue

            # Otherwise, return block pos
            return block_pos

        # Default to returning None
        return None

    # Push an entity out of any adjacent blocks
    # Returns block position, -1, or None for block, entity, and no collision
    def _push_out( self, is_x_axis ):

        xy = 'x' if is_x_axis else 'y' # Reduce boilerplate code

        # Check for entities before blocks
        entity = self.is_inside_entity()
        if ( entity is not None ):

            is_rightward_push = eval( f'self.pos.{xy} > entity.pos.{xy}' )
            push_offset = eval( f'entity.hitbox.{xy} - self.hitbox_offset.{xy}' ) if is_rightward_push else eval( f'-self.hitbox.{xy} - self.hitbox_offset.{xy}' )
            exec( f'self.pos.{xy} = entity.pos.{xy} + entity.hitbox_offset.{xy} + push_offset' )
            return -1

        block_pos = self.is_inside_block()
        if ( block_pos is None ):
            return None

        block_id = self.controller.get_block_type( block_pos )

        # Push out based on their position within the block
        # The is_x_axis argument determines the axis it's pushed along
        is_rightward_push = eval( f'self.pos.{xy} > block_pos.{xy}' )
        push_offset = eval( f'1 - self.hitbox_offset.{xy}' ) if is_rightward_push else eval( f'-self.hitbox.{xy} - self.hitbox_offset.{xy}' )
        exec( f'self.pos.{xy} = block_pos.{xy} + push_offset' )
        return block_pos

    # Returns a list of the vectors of any block position the entity
    def get_adjacent_blocks( self ):

        output = []

        bound_1 = self.pos.c().a( self.hitbox_offset ).a( COLLISION_EPSILON )
        bound_2 = self.pos.c().a( self.hitbox_offset ).a( self.hitbox ).s( COLLISION_EPSILON )

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
    def x_push_func( self, block_pos ):
        pass

    # Same as before, but for vertical collisions
    def y_push_func( self, block_pos ):
        pass

    # Executes for each block the player is inside of
    def collision_func( self, block_pos ):
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