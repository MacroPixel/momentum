from basic_imports import *
from entity_list import *

def update_abilities( self ):

    # UP key press = invert ability
    if ( self.engine.get_key( BINDS[ 'up_action' ], 1 ) ):
        self.use_ability( 'invert', self.invert )

    # DOWN key press could be 3 different abilities
    if ( self.engine.get_key( BINDS[ 'down_action' ], 1 ) ):

        # Hook if possible
        if ( self.has_ability( 'rope' ) and self.rope_check() is not None ):
            self.use_ability( 'rope', self.rope_hook )

        # Otherwise, pick up object if on floor
        elif ( self.has_ability( 'slot' ) and self.is_on_solid() ):
            self.use_ability( 'slot', self.slot_use )

        # Otherwise, default to stomping
        else:
            self.use_ability( 'stomp', self.stomp )

    # DOWN key release = unhook
    if ( self.engine.get_key( BINDS[ 'down_action' ], 2 ) ):
        self.rope_unhook()

    # LEFT + RIGHT hold = glide
    if ( self.engine.get_key( BINDS[ 'right_action' ] ) and self.engine.get_key( BINDS[ 'left_action' ] ) ):
        self.use_ability( 'glide', self.glide )

    # Additional physics if using hook ability
    if ( self.hook_obj is not None ):

        self.vel.a( self.hook_obj.get_acceleration().m( self.engine.delta_time ) )
        self.vel.m( 0.8 ** self.engine.delta_time )

# Functions to modify and query abilities
def grant_ability( self, string ):
    self._has_ability[ string ] = True

def revoke_ability( self, string ):
    self._has_ability[ string ] = False

def has_ability( self, string ):
    return self._has_ability[ string ]

# Runs the inputted function if the player has a certain ability
def use_ability( self, ability_string, ability_function, require_ability = True ):

    # Enforce ability check (can be disabled via 'require_ability')
    if ( require_ability and not self.has_ability( ability_string ) ):
        return

    ability_function()

# Rotates velocity vector 90 degrees counterclockwise
def invert( self ):

    self.vel.x, self.vel.y = self.vel.y, -self.vel.x

# Quickly charges down, allowing enemies to be destroyed
def stomp( self ):

    self.vel.y = max( 60, self.vel.y )

# Switches inventory slot with closest pickupable item
# Works if no item in slot or no pickupable item
def slot_use( self ):

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
def rope_check( self ):

    for hook in self.engine.get_instances( 'rope_hook' ):
        if utils.collision_check( self.pos.c(), hook.pos.c(), self.hitbox.c(), hook.hitbox.c(), self.hitbox_offset.c(), hook.hitbox_offset.c() ):
            return hook

    return None

# Initially latches onto a rope hook object
# Player must be touching the hook's 3x3 hitbox
def rope_hook( self ):

    # Store a reference to the nearest hook
    hook_obj = self.rope_check()
    if ( hook_obj is not None ):
        self._hook_obj = hook_obj

# Unhooks from the current hook object
def rope_unhook( self ):

    if ( self.hook_obj is not None ):

        # First, apply a large "elastic force" to the velocity
        # I know this isn't realistic, but it's fun, so idc
        self.vel.a( self.hook_obj.get_acceleration().d( 5 ).fn( lambda a: abs( a ) ** 1.3 * ( -1 if a < 0 else 1 ) ) )

        # Then, relinquish the reference to the hook
        self._hook_obj = None

# Limits y acceleration to 5
def glide( self ):

    self.vel.y = min( 5, self.vel.y )