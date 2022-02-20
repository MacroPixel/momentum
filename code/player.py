from basic_imports import *
from entity import *
import random

# It's you :D
class Player ( Entity ):

    def __init__( self, engine, spawn_pos, abilities ):

        super().__init__( engine, 'player', spawn_pos, V2(), ( 44 / 48, 44 / 48, 2 / 48, 4 / 48 ), LAYER_PLAYER )
        self.entity_destroy_on_death = False
        self._reset_basic_vars()

        # Stores whether the player has each ability
        # Then, grant abilities present in metadata
        self._has_ability = { ability: False for ability in ABILITY_STRINGS }
        for ability_id in abilities:
            self.grant_ability( ABILITY_STRINGS[ ability_id ], do_file_update = False )

        # Other variables
        self._checkpoint_pos = spawn_pos
        self._can_invert = False
        self._is_stomping = False
        self._can_teleport = False
        self._hook_obj = None
        self._slot_item = -1
        self._has_intially_set_view = False
        self._wall_vel = V2() # Stores the velocity before the collision event
        self._debug_grab = False # When the player is being moved with the cursor

        # Debug variables
        self._is_invincible = False

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

        # Set the view once after the controller is created
        if not self._has_intially_set_view:
            self.engine.get_instance( 'controller' ).view_pos = self.pos.c().m( GRID ).a( 0.5, 0.5 )
            self._has_intially_set_view = True

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
            # Skip if debugging
            if ( not self._debug_grab ):
                super().entity_update()

        # Update view regardless
        controller = self.engine.get_instance( 'controller' )
        new_view = controller.view_pos
        new_view.x = utils.lerp( new_view.x, ( self.pos.x + 0.5 ) * GRID, 0.85, self.engine.delta_time * 10 )
        new_view.y = utils.lerp( new_view.y, ( self.pos.y + 0.5 ) * GRID, 0.85, self.engine.delta_time * 10 )
        new_view.fn( lambda a: round( a, 2 ) )
        controller.view_pos = new_view

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
        released_jump = ( self.has_released_jump == 0 )
        if ( self.engine.get_key( BINDS[ 'jump' ] ) and self.is_on_solid() and released_jump ):

            # Jump
            self.vel.y = -PLAYER_JUMP_POWER

            # Jumping also gives a boost to horizontal speed
            if self.is_on_solid() and self.engine.get_key( BINDS[ 'move_right' ] ):
                self.vel.x += PLAYER_HSPEED_BOOST
            elif self.is_on_solid() and self.engine.get_key( BINDS[ 'move_left' ] ):
                self.vel.x -= PLAYER_HSPEED_BOOST

        # Also can get smaller boost from water
        elif ( self.is_in_fluid() and self.engine.get_key( BINDS[ 'jump' ], 1 ) and released_jump ):
            self.vel.y = min( self.vel.y, -PLAYER_SWIM_POWER )

        # Water reduces the amount of gravity
        self.entity_gravity_multiplier = 0.4 if self.is_in_fluid() else 1

        # DEBUG ABILITY: Teleport to cursor
        if ( self.engine.get_instance( 'controller' ).debug and self.engine.get_mouse_button( 1 ) ):
            self.pos = self.engine.get_world_cursor().d( GRID )
            self.vel = V2()
            self._debug_grab = True
        else:
            self._debug_grab = False

    # Check which entities the player is colliding with
    # Includes hazards and checkpoints
    def update_collisions( self ):

        # Skip if debugging
        if ( self._debug_grab ):
            return

        # If touching hazardous entity, die
        for entity in self.engine.get_tagged_instances( 'hazardous' ):
            if utils.collision_check( self.pos, entity.pos, self.hitbox, entity.hitbox ):

                # Kill the enemy if possible
                if entity.has_tag( 'enemy' ) and self.is_stomping:
                    entity.die()

                # Otherwise, kill the player
                else:
                    self.die()

        # If touching non-current checkpoint, update the current checkpoint
        for checkpoint in self.engine.get_instances( 'checkpoint' ):
            if utils.collision_check( self.pos, checkpoint.pos, self.hitbox, checkpoint.hitbox ):
                self.set_checkpoint( checkpoint.real_pos )

        # If touching powerup, give the player the ability and delete the powerup
        for powerup in self.engine.get_instances( 'powerup' ):
            if utils.collision_check( self.pos, powerup.pos, self.hitbox, powerup.hitbox ):

                # Show tooltip if this is the first ability
                if len( [ True for a in self._has_ability if self._has_ability[ a ] ] ) == 0:
                    self.engine.get_instance( 'controller' ).show_ability_tooltip( 5 )

                self.grant_ability( ABILITY_STRINGS[ powerup.ability_id ] )
                powerup.delete()

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
    from _player_abilities import update_abilities
    from _player_abilities import ability_invert
    from _player_abilities import ability_wall_jump
    from _player_abilities import ability_stomp
    from _player_abilities import ability_teleport
    from _player_abilities import ability_slot
    from _player_abilities import ability_rope
    from _player_abilities import ability_glide
    from _player_abilities import _resolve_down_press
    from _player_abilities import _slot_set
    from _player_abilities import _try_pickup
    from _player_abilities import _drop_item
    from _player_abilities import _rope_check
    from _player_abilities import _rope_unhook
    
    # Creates an object that displays UI and eventually restarts the level
    def die( self ):

        # Don't die if invincible or debugging
        if ( self.is_invincible or self._debug_grab ):
            return

        # Death effects
        controller = self.engine.get_instance( 'controller' )
        for i in range( 25 ):
            self.engine.get_instance( 'controller' )._Controller__c_particle.create_simple(
                self.pos.c().a( 0.5 ), ( 2, 6 ), ( 0, 360 ), ( 1, 2 ), [ ( 200, 0, 0 ), ( 150, 0, 0 ), ( 180, 0, 0 ) ], ( 0.4, 0.9 ), ( 1.5, 2 ) )
        self._is_alive = False
        controller.new_death_string()
        controller.shake_screen( 2, 0.3 )
        self.engine.play_sound( 'death' )

        # Unhook rope
        self._hook_obj = None

        # Store death in controller
        controller.set_level_meta( 'deaths', controller.get_level_meta( 'deaths' ) + 1 )

        # Parent event
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

        # Write position to file
        self.engine.get_instance( 'controller' ).set_level_meta( 'player_spawn', self._checkpoint_pos.l() )

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

        # Draw the rope hook if player is using it
        if ( self.hook_obj is not None ):
            self.engine.draw_line( self.pos.c().m( GRID ).a( GRID / 2 ), self.hook_obj.pos.c().m( GRID ).a( GRID / 2 ), False, ( 125, 99, 75 ), is_aa = True )

        # Draw the actual player
        draw_pos = self.pos.c().m( GRID )
        if ( self._image_attack > 0 ):
            draw_image = V2( 2, min( 2, 2 - floor( self.image_attack ) ) )
        elif abs( self.vel.x ) < 0.5:
            draw_image = V2( 0, floor( self.image_bob ) % 2 )
        else:
            draw_image = V2( 1, floor( self.image_walk ) % 8 )
        self.engine.draw_sprite( 'player', draw_image, draw_pos.c(), False, flip = V2( self.image_dir, 1 ) )

        # Draw the player's item above their head if they have one
        if ( self.slot_item != -1 ):

            self.engine.draw_sprite( 'items', V2( 0, self.slot_item ), draw_pos.c().s( 0, 16 ), False )

        # Store the sprite for usage in ragdoll
        self.update_ragdoll( 'player', draw_pos.c().d( GRID ), self.image_dir == -1 )

    # Checks if a block matching a condition is below the player
    def test_block_below( self, condition = lambda a: True ):

        controller = self.engine.get_instance( 'controller' )
        x_min_bound = self.pos.x + self.hitbox_offset.x
        x_max_bound = self.pos.x + self.hitbox_offset.x + self.hitbox.x
        for xx in range( floor( x_min_bound + COLLISION_EPSILON ), ceil( x_max_bound - COLLISION_EPSILON ) ):
            pos = V2( xx, floor( self.pos.y + self.hitbox_offset.y + self.hitbox.y + COLLISION_EPSILON ) )
            if ( controller.is_block( pos ) ):
                block_id = controller.get_block_type( pos )
                if ( condition( block_id ) ):
                    return True
        return False

    # Checks if a block matching a condition is beside the player
    def test_block_beside( self, to_left = True, condition = lambda a: True ):

        controller = self.engine.get_instance( 'controller' )
        y_min_bound = self.pos.y + self.hitbox_offset.y
        y_max_bound = self.pos.y + self.hitbox_offset.y + self.hitbox.y
        hitbox_x = 0 if to_left else self.hitbox.x
        epsilon_x = COLLISION_EPSILON * ( -1 if to_left else 1 )
        for yy in range( floor( y_min_bound + COLLISION_EPSILON ), ceil( y_max_bound - COLLISION_EPSILON ) ):
            pos = V2( floor( self.pos.x + self.hitbox_offset.x + hitbox_x + epsilon_x ), yy )
            if ( controller.is_block( pos ) ):
                block_id = controller.get_block_type( pos )
                if ( condition( block_id ) ):
                    return True
        return False

    # Shorthand for checking solid block below player
    # Also includes solid entities
    def is_on_solid( self ):

        temp_offset = self.hitbox_offset.c().a( 0, self.hitbox.y )
        for entity in self.engine.get_tagged_instances( 'solid_entity' ):
            if ( utils.collision_check( self.pos.c(), entity.pos.c(), V2( self.hitbox.x, COLLISION_EPSILON ), entity.hitbox, temp_offset, entity.hitbox_offset ) ):
                return True

        if self.test_block_below( lambda block_id: utils.b_string( block_id ) not in B_PASSABLE ):
            return True

        return False

    # Shorthand for checking solid block beside player
    def is_beside_solid( self, to_left ):

        return self.test_block_beside( to_left, lambda block_id: utils.b_string( block_id ) not in B_PASSABLE )

    # Shorthand for checking if any part of the player is in a fluid
    def is_in_fluid( self ):

        controller = self.engine.get_instance( 'controller' )
        for block_pos in self.get_adjacent_blocks():
            if controller.is_block( block_pos ) and utils.b_string( controller.get_block_type( block_pos ) ) in B_FLUID:
                return True
        return False

    # Checks a sample of blocks around the player to see the most numerous one
    # This then returns an region ID for the controller to use
    def get_region( self ):

        controller = self.engine.get_instance( 'controller' )
        block_ids = []

        # Store the position of any non-empty blocks in a 5x5 square
        pos = self.pos.c().i()
        for xx in range( pos.x - 2, pos.x + 2 ):
            for yy in range( pos.y - 2, pos.y + 2 ):
                if controller.is_block( V2( xx, yy ) ):
                    block_ids.append( controller.get_block_type( V2( xx, yy ) ) )

        # -1 indicates no specific region (i.e. empty/inconclusive list)
        if len( block_ids ) == 0:
            return -1

        # Find the mode and attempt to map it to an region ID
        mode = utils.b_string( max( set( block_ids ), key = block_ids.count ) )
        for i, _ in enumerate( REGION_STRINGS ):
            if mode in REGION_BLOCKS[ i ]:
                return i
        return -1

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

    @property
    def slot_item( self ):
        return self._slot_item

    @property
    def slot_item_str( self ):
        if self.slot_item == -1:
            return None
        return ITEM_STRINGS[ self.slot_item ]

    @property
    def can_invert( self ):
        return self._can_invert

    @property
    def is_stomping( self ):
        return self._is_stomping

    @property
    def can_teleport( self ):
        return self._can_teleport

    @property
    def wall_vel( self ):
        return self._wall_vel