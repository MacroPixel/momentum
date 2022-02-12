from basic_imports import *
from entity import *

# It's you :D
class Player ( Entity ):

    def __init__( self, engine ):

        super().__init__( engine, 'player', V2(), V2(), ( 44 / 48, 44 / 48, 2 / 48, 4 / 48 ), LAYER_PLAYER )
        self.entity_destroy_on_death = False

        self._reset_basic_vars()

        # Stores whether the player has each ability
        self._has_ability = { ability: False for ability in ABILITY_STRINGS }

        # Other variables
        self._checkpoint_pos = V2( 0, 0 )
        self._hook_obj = None

        # Debug variables
        self._is_invincible = False

        # Automatically give all abilities
        for ability in ABILITY_STRINGS:
            if not self.has_ability( ability ):
                self.grant_ability( ability )

    # Allows easy initializing/resetting of a group of variables
    def _reset_basic_vars( self ):

        # Store image & physics details
        self._image_dir = 1
        self._image_walk = 0
        self._image_bob = 0
        self._image_attack = 0
        self._has_released_jump = 5

        # Other vars
        self._is_alive = True
        self.vel = V2( 0, 0 )

    def update( self ):

        # Cancel if game is paused
        if ( self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL ):
            return

        # Only perform gameplay actions if player is alive
        if ( self.is_alive ):

            # Only alters velocity
            # Position is calculated during entity_update()
            self.update_movement()

            # Alters velocity further as well as other variables
            self.update_abilities()

            # Check collisions with other entities
            self.update_collisions()

            # Choose which animation frame to use during draw event
            self.update_image()

            # Controlls velocity, collisions, and interactions with other enemies
            super().entity_update()

        # Update view regardless
        self.engine.view_pos.x = utils.lerp( self.engine.view_pos.x, ( self.pos.x + 0.5 ) * GRID, 0.85, self.engine.delta_time * 10 )
        self.engine.view_pos.y = utils.lerp( self.engine.view_pos.y, ( self.pos.y + 0.5 ) * GRID, 0.85, self.engine.delta_time * 10 )
        self.engine.view_pos.fn( lambda a: round( a, 2 ) )

    # Alter the player's velocity
    def update_movement( self ):
        
        # Horizontal momentum
        # PLAYER_HSPEED defines the base speed
        # The player experiences a deficit of momentum when they're not standing on a block
        # This is defined as PLAYER_HSPEED_AIR_FACTOR
        # Friction (only when on block) works by pretending they're holding the key
        # in the opposite direction they're moving
        velocity_factor = 1
        if ( not self.is_on_solid() ):
            velocity_factor *= PLAYER_HSPEED_AIR_FACTOR
        if ( self.engine.get_key( BINDS[ 'move_right' ] ) ):
            self.vel.x += PLAYER_HSPEED * self.engine.delta_time * velocity_factor
        elif ( self.engine.get_key( BINDS[ 'move_left' ] ) ):
            self.vel.x -= PLAYER_HSPEED * self.engine.delta_time * velocity_factor
        elif self.is_on_solid():
            self.vel.x = max( abs( self.vel.x ) - ( PLAYER_HSPEED * self.engine.delta_time * velocity_factor ), 0 ) * ( -1 if self.vel.x < 0 else 1 )

        # Since space is used to switch rooms/respawn, the player will sometimes
        # automatically jump upon loading in
        # This variable waits for it to be released for 5 frames to prevent that from happening
        if ( self.has_released_jump > 0 and not self.engine.get_key( BINDS[ 'jump' ] ) ):
            self._has_released_jump -= 1

        # Vertical momentum
        can_jump = ( self.is_on_solid() and self.engine.get_key( BINDS[ 'jump' ] ) and self.has_released_jump == 0 )
        if ( can_jump ):

            # Jump
            self.vel.y = -PLAYER_JUMP_POWER

            # Jumping also gives a boost to horizontal speed
            if self.is_on_solid() and self.engine.get_key( BINDS[ 'move_right' ] ):
                self.vel.x += PLAYER_HSPEED_BOOST
            elif self.is_on_solid() and self.engine.get_key( BINDS[ 'move_left' ] ):
                self.vel.x -= PLAYER_HSPEED_BOOST

    # Update the player's variables via unlocked abilities
    from _player_abilities import update_abilities

    # Check which entities the player is colliding with
    # Includes hazards and checkpoints
    def update_collisions( self ):

        # Doesn't apply if invincible
        if ( self.is_invincible ):
            return

        # If touching enemy, die
        for enemy in self.engine.get_tagged_instances( 'enemy' ):
            if utils.collision_check( self.pos, enemy.pos, self.hitbox, enemy.hitbox ) and enemy.enemy_kills_player:
                self.die()

        # If touching non-current checkpoint, update the current checkpoint
        for checkpoint in self.engine.get_instances( 'checkpoint' ):
            if utils.collision_check( self.pos, checkpoint.pos, self.hitbox, checkpoint.hitbox ):
                self.set_checkpoint( checkpoint.real_pos )

    # Make the player bob, walk, swing, etc.
    def update_image( self ):

        # Set image details
        # Walk is incremented while velocity >= 0.5, otherwise head bob is incremented
        self._image_walk += abs( self.vel.x ) * self.engine.delta_time * 3
        if abs( self.vel.x ) < 0.5:
            self._image_walk = 0
        if abs( self.vel.x ) < 0.5 and self.is_on_solid():
            self._image_bob += self.engine.delta_time * 0.8
        else:
            self._image_bob = 0
        if ( self.vel.x ) < -0.01:
            self._image_dir = -1
        elif ( self.vel.x > 0.01 ):
            self._image_dir = 1

        # If attack is > 0, it goes through 1 frame every 0.05 seconds
        if ( self.image_attack > 0 ):
            self._image_attack = max( 0, self._image_attack - self.engine.delta_time / 0.05 )

    # Abilities
    from _player_abilities import grant_ability
    from _player_abilities import revoke_ability
    from _player_abilities import has_ability
    from _player_abilities import use_ability
    from _player_abilities import invert
    from _player_abilities import stomp
    from _player_abilities import rope_check
    from _player_abilities import rope_hook
    from _player_abilities import rope_unhook
    from _player_abilities import glide
    
    # Creates an object that displays UI and eventually restarts the level
    def die( self ):

        for i in range( 25 ):
            self.engine.get_instance( 'controller' )._Controller__c_particle.create_simple(
                self.pos.c().a( 0.5 ), ( 2, 6 ), ( 0, 360 ), ( 1, 2 ), [ ( 200, 0, 0 ), ( 150, 0, 0 ), ( 180, 0, 0 ) ], ( 0.4, 0.9 ), ( 1.5, 2 ) )
        self._is_alive = False
        self.engine.get_instance( 'controller' ).new_death_string()
        self.engine.play_sound( 'death' )
        super().die()

    # Updates the checkpoint (if necessary) & plays sound effect
    def set_checkpoint( self, new_pos ):

        # Don't set a checkpoint twice
        # This would cause the sound effect to repeatedly play
        # Also, comparing two floating point values with == is okay
        # because one is directly copied from the other
        if ( self.checkpoint_pos == new_pos ):
            return

        # Update the checkpoint position
        self._checkpoint_pos = new_pos

        # Play the sound
        self.engine.play_sound( 'checkpoint' )

    # Teleports the player to their checkpoint position
    # and resets some of their variables
    def load_checkpoint( self ):

        self.pos = self.checkpoint_pos
        self._reset_basic_vars()

    # Draw self at current position
    # Leverages flip operations & sub-images
    # Also drawn slightly higher than the player's position because its hitbox isn't centered
    def draw( self ):

        # Don't draw unless alive
        if ( not self.is_alive ):
            return

        draw_pos = self.pos.c().m( GRID )

        # Only execute if player is using rope hook
        if ( self.hook_obj is not None ):

            # Draw rope
            self.engine.draw_line( self.pos.c().m( GRID ).a( GRID / 2 ), self.hook_obj.pos.c().m( GRID ).a( GRID / 2 ), False, ( 125, 99, 75 ), is_aa = True )

        # Detemine which animation to use
        if ( self._image_attack > 0 ):
            draw_image = V2( 2, min( 2, 2 - floor( self.image_attack ) ) )
        elif abs( self.vel.x ) < 0.5:
            draw_image = V2( 0, floor( self.image_bob ) % 2 )
        else:
            draw_image = V2( 1, floor( self.image_walk ) % 8 )

        # Actually draw the player
        self.engine.draw_sprite( 'player', draw_image, draw_pos.c(), False, flip = V2( self.image_dir, 1 ) )

        # Store the sprite for usage in ragdoll
        self.update_ragdoll( 'player', draw_pos.c().d( GRID ), self.image_dir == -1 )

    # Checks if a block matching a condition is below the player
    def test_block_below( self, condition = lambda a: True ):

        controller = self.engine.get_instance( 'controller' )
        x_min_bound = self.pos.x + self.hitbox_offset.x
        x_max_bound = self.pos.x + self.hitbox_offset.x + self.hitbox.x
        for xx in range( floor( x_min_bound + COLLISION_EPSILON ), ceil( x_max_bound - COLLISION_EPSILON ) ):
            pos = V2( xx, floor( self.pos.y + self.hitbox_offset.y + self.hitbox.y ) )
            if ( controller.is_block( pos ) ):
                block_id = utils.obj_id_to_block( controller.get_object_type( pos ) )
                if ( condition( block_id ) ):
                    return True
        return False

    # Shorthand for checking solid block below player
    def is_on_solid( self ):

        return self.test_block_below( lambda block_id: utils.b_string( block_id ) not in B_PASSABLE )

    @property
    def image_dir( self ):
        return self._image_dir

    @property
    def image_walk( self ):
        return self._image_walk

    @property
    def image_attack( self ):
        return self._image_attack

    @property
    def image_bob( self ):
        return self._image_bob

    @property
    def is_alive( self ):
        return self._is_alive

    @property
    def is_invincible( self ):
        return self._is_invincible

    @is_invincible.setter
    def is_invincible( self, value ):
        self._is_invincible = bool( value )

    @property
    def has_released_jump( self ):
        return self._has_released_jump

    @property
    def checkpoint_pos( self ):
        return self._checkpoint_pos

    @property
    def hook_obj( self ):
        return self._hook_obj