from basic_imports import *

def update_abilities( self ):
    # Invert ability
    if ( self.engine.get_key( BINDS[ 'up_action' ], 1 ) ):
        self.use_ability( 'invert', self.invert )

    # Down key (hook/stomp)
    if ( self.engine.get_key( BINDS[ 'down_action' ], 1 ) ):

        # Hook if possible
        if ( self.has_ability( 'rope' ) and self.rope_check() is not None ):
            self.use_ability( 'rope', self.rope_hook )

        # Otherwise, default to stomping
        else:
            self.use_ability( 'stomp', self.stomp )

    # Unhook if down key is released
    if ( self.engine.get_key( BINDS[ 'down_action' ], 2 ) ):

        self.rope_unhook()

    # Add acceleration if rope is currently hooked
    if ( self.hook_obj is not None ):

        self.vel.a( self.hook_obj.get_acceleration().m( self.engine.delta_time ) )
        self.vel.m( 0.8 ** self.engine.delta_time )

    # Glide ability
    if ( self.engine.get_key( BINDS[ 'right_action' ] ) and self.engine.get_key( BINDS[ 'left_action' ] ) ):
        self.use_ability( 'glide', self.glide )

def grant_ability( self, string ):

    self._has_ability[ string ] = True

def revoke_ability( self, string ):

    self._has_ability[ string ] = False

def has_ability( self, string ):

    return self._has_ability[ string ]

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
        self.vel = self.hook_obj.get_acceleration().d( 5 ).fn( lambda a: abs( a ) ** 1.3 * ( -1 if a < 0 else 1 ) )

        # Then, relinquish the reference to the hook
        self._hook_obj = None

# Limits y acceleration to 5
def glide( self ):

    self.vel.y = min( 5, self.vel.y )