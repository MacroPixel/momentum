from basic_imports import *
from entity_list import *

# Functions to modify and query abilities
def grant_ability( self, string ):
    self._has_ability[ string ] = True

def revoke_ability( self, string ):
    self._has_ability[ string ] = False

def has_ability( self, string ):
    return self._has_ability[ string ]

# Runs each ability event, passing in whether the player has permission to use it
def update_abilities( self ):

    # Delegate updates to other functions
    self.ability_invert( self.has_ability( 'invert' ) )
    self.ability_wall_jump( self.has_ability( 'wall_jump' ) )
    self.ability_stomp( self.has_ability( 'stomp' ) )
    self.ability_teleport( self.has_ability( 'teleport' ) )
    self.ability_slot( self.has_ability( 'slot' ) )
    self.ability_rope( self.has_ability( 'rope' ) )
    self.ability_glide( self.has_ability( 'glide' ) )

# Rotates the velocity vector 90 degrees CCW
def ability_invert( self, has_ability = True ):

    # Fires when up is pressed
    if ( has_ability and self.engine.get_key( BINDS[ 'up_action' ], 1 ) and self.can_invert ):
        self.vel.x, self.vel.y = self.vel.y, -self.vel.x
        self._can_invert = False

    # The player's ability refreshes when they're on a solid block
    if ( self.is_on_solid() ):
        self._can_invert = True

# Reflects x-velocity off a wall and gives a y-velocity boost
def ability_wall_jump( self, has_ability = True ):

    # Must hold right/left key
    right_hold = self.engine.get_key( BINDS[ 'right_action' ] )
    left_hold = self.engine.get_key( BINDS[ 'left_action' ] )
    if ( has_ability and ( right_hold or left_hold ) ):

        # Make sure the player is next to the correct wall
        left_hold = self.engine.get_key( BINDS[ 'left_action' ], 0 )
        right_hold = self.engine.get_key( BINDS[ 'right_action' ], 0 )
        has_grip_left = ( left_hold and self.is_beside_solid( to_left = True ) and self.engine.get_key( BINDS[ 'move_left' ] ) )
        has_grip_right = ( right_hold and self.is_beside_solid( to_left = False ) and self.engine.get_key( BINDS[ 'move_right' ] ) )
        if ( ( has_grip_left or has_grip_right ) and abs( self.wall_vel.x ) > PLAYER_MIN_WALL_VEL ):

            # Reflect position and apply jump boost
            # Position is clamped so its magnitude doesn't exceed PLAYER_MAX_WALL_VEL
            self.vel.x = min( max( -PLAYER_MAX_WALL_VEL, -self.wall_vel.x ), PLAYER_MAX_WALL_VEL )
            self.vel.y = -PLAYER_JUMP_POWER

    # Store the current velocity for next update
    self._wall_vel = self.vel.c()

# Quickly charges down, allowing enemies to be destroyed
def ability_stomp( self, has_ability = True ):

    if ( has_ability and self._resolve_down_press() == 'stomp' ):
        self.vel.y = max( 60, self.vel.y )

# Moves the player forward in the direction of their current velocity
# Only goes through passable blocks and entities
def ability_teleport( self, has_ability = True ):

    # In total, the player moves 0.25s worth of distance
    # It uses the entity class' collision methods to move,
    # but disables the normal entity/hazard events
    if ( has_ability and self._resolve_down_press() == 'teleport' and self.can_teleport ):
        
        self.entity_dies_to_hazards = False
        self.shift_pos( self.vel.c().m( 0.25 ) )
        self.entity_dies_to_hazards = True
        self._can_teleport = False

    # The player's ability refreshes when they're on a solid block
    if ( self.is_on_solid() ):
        self._can_teleport = True

# Picks up item near player/drops current item
def ability_slot( self, has_ability = True ):

    # Occurs when the player presses down
    if ( has_ability and self._resolve_down_press() == 'slot' ):

        # Store what item used to be in the slot
        prev_item = self.slot_item

        # Pick up the closest pickupable item
        min_dist = 5
        nearest_obj = None
        for entity in self.engine.get_tagged_instances( 'pickupable' ):
            dist = utils.dist( self.pos.c(), entity.pos.c() )
            if dist < min_dist:
                min_dist = dist
                nearest_obj = entity

        if nearest_obj is not None:
            self._slot_set( nearest_obj.pickup() )
        else:
            self._slot_set( -1 )

        # Drop the previous item
        if ( prev_item != -1 ):
            self._drop_item( prev_item )

# Allows the player to hook onto a rope and swing from it
# This method also handles other rope updates
def ability_rope( self, has_ability = True ):

    # Store a reference to the nearest hook
    if ( has_ability and self._resolve_down_press() == 'rope' ):
        hook_obj = self._rope_check()
        if ( hook_obj is not None ):
            self._hook_obj = hook_obj

    # Release hook if down is pressed
    if ( self.engine.get_key( BINDS[ 'down_action' ], 2 ) ):
        self._rope_unhook()

    # Additional physics if hooked onto rope
    if ( self.hook_obj is not None ):

        self.vel.a( self.hook_obj.get_acceleration().m( self.engine.delta_time ) )
        self.vel.m( 0.8 ** self.engine.delta_time )

# Limits y acceleration to 5
def ability_glide( self, has_ability = True ):

    # Occurs when player holds down left and right key
    if ( has_ability and len( [ key_str for key_str in [ 'left_action', 'right_action' ] if self.engine.get_key( BINDS[ key_str ] ) ] ) == 2 ):
        self.vel.y = min( 5, self.vel.y )

# There are multiple abilities that use the down key,
# so this function decides which one should be used
def _resolve_down_press( self ):

    # Do nothing if down key wasn't pressed
    if ( not self.engine.get_key( BINDS[ 'down_action' ], 1 ) ):
        return None

    # Is the player within range of a rope hook?
    if ( self._rope_check() is not None ):
        return 'rope'

    # Is the player on the ground?
    elif ( self.is_on_solid() ):
        return 'slot'

    # Is the player holding space?
    elif ( self.engine.get_key( BINDS[ 'jump' ] ) ):
        return 'stomp'

    # Default to 'teleport'
    return 'teleport'

# Changes the item in the player's inventory slot
# Can use an integer ID, a string, or None
# Only should be called internally
def _slot_set( self, value ):

    if isinstance( value, str ):
        self._slot_item = ITEM_STRINGS.index( value )
    elif value is None:
        self._slot_item = -1
    else:
        self._slot_item = max( -1, int( value ) )

# Creates an entity from its corresponding item ID
def _drop_item( self, item_id ):

    entity_id = ENTITY_STRINGS.index( ITEM_ENTITIES[ item_id ] )
    engine_ref = self.engine
    entity_pos = self.pos.c().a( self.image_dir, 0 )
    dropped_obj = eval( f"{ ENTITY_CLASSES[ entity_id ] }( engine_ref, entity_pos )" )
    dropped_obj.on_drop()

# Returns a hook object within range of the player
# If no hook is within range, it returns None
def _rope_check( self ):

    for hook in self.engine.get_instances( 'rope_hook' ):
        if utils.collision_check( self.pos.c(), hook.pos.c(), self.hitbox.c(), hook.hitbox.c(), self.hitbox_offset.c(), hook.hitbox_offset.c() ):
            return hook

    return None

# Unhooks from the current hook object
def _rope_unhook( self ):

    if ( self.hook_obj is not None ):

        # First, apply a large "elastic force" to the velocity
        # I know this isn't realistic, but it's fun, so idc
        self.vel.a( self.hook_obj.get_acceleration().d( 5 ).fn( lambda a: abs( a ) ** 1.3 * ( -1 if a < 0 else 1 ) ) )

        # Then, relinquish the reference to the hook
        self._hook_obj = None