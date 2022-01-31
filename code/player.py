from basic_imports import *

# It's you :D
class Player ( Game_Object ):

    def __init__( self, engine ):

        # Store image & physics details
        super().__init__( engine, 'player', layer = 1 )
        self._image_dir = 1
        self._image_walk = 0
        self._image_bob = 0
        self._pos = V2()
        self._vel = V2()

    def update( self ):

        # Don't bother if game is paused
        if self.engine.get_instance( 'controller' ).pause_level >= PAUSE_NORMAL:
            return
        
        # Horizontal momentum
        if self.engine.get_key( BINDS[ 'move_right' ] ):
            self.vel.x += PLAYER_HSPEED * self.engine.delta_time
        elif self.engine.get_key( BINDS[ 'move_left' ] ):
            self.vel.x -= PLAYER_HSPEED * self.engine.delta_time
        elif self.is_on_block():
            self.vel.x *= ( 1 / PLAYER_FRICTION ) ** self.engine.delta_time

        # Vertical momentum
        can_jump = ( self.is_on_block() and self.engine.get_key( BINDS[ 'jump' ] ) )
        if ( can_jump ):

            # Jump
            self.vel.y = -PLAYER_JUMP_POWER

            # Jumping also gives a boost to horizontal speed
            if self.is_on_block() and self.engine.get_key( BINDS[ 'move_right' ] ):
                self.vel.x += PLAYER_HSPEED_BOOST
            elif self.is_on_block() and self.engine.get_key( BINDS[ 'move_left' ] ):
                self.vel.x -= PLAYER_HSPEED_BOOST

        self.vel.y += GRAVITY * self.engine.delta_time

        # Abilities
        if ( self.engine.get_key( BINDS[ 'attack' ], 1 ) ):
            self.attack()

        if ( self.engine.get_key( BINDS[ 'invert' ], 1 ) ):
            self.invert()

        # Set image details
        # Walk is incremented while velocity >= 0.2, otherwise head bob is incremented
        self._image_walk += abs( self.vel.x ) * self.engine.delta_time * 3
        if abs( self.vel.x ) < 0.5:
            self._image_walk = 0
        if abs( self.vel.x ) < 0.5 and self.is_on_block():
            self._image_bob += self.engine.delta_time * 0.8
        else:
            self._image_bob = 0
        if ( self.vel.x ) < -0.01:
            self._image_dir = -1
        elif ( self.vel.x > 0.01 ):
            self._image_dir = 1

        # Actually move
        # Perform collision detection on the 4 adjacent blocks
        # This is done with multiple iterations to make it more precise
        vel_factor = V2( 1, 1 )

        iterations = 5
        for i in range( iterations ):

            self.pos.x += self.vel.x * self.engine.delta_time / iterations
            self.push_out( is_x_axis = True )

            self.pos.y += self.vel.y * self.engine.delta_time / iterations
            self.push_out( is_x_axis = False )

        # Update view
        self.engine.view_pos = self.pos.c().m( GRID )

    # ABILITIES

    def attack( self ):

        # Comes at a cost of velocity
        self.vel.x *= PLAYER_HSPEED_ATTACK_FACTOR

    # Rotates velocity vector 90 degrees counterclockwise
    def invert( self ):

        self.vel.x, self.vel.y = self.vel.y, -self.vel.x

    # Draw self at current position
    # Leverages flip operations & sub-images
    # Also drawn slightly higher than the player's position because its hitbox isn't centered
    def draw( self ):

        if abs( self.vel.x ) < 0.5:
            self.engine.draw_sprite( 'player', V2( 0, floor( self.image_bob ) % 2 ), self.pos.c().s( 0, ( 1 - PLAYER_HITBOX[1] ) / 2 ).m( GRID ), False, flip = V2( self.image_dir, 1 ) )
        else:
            self.engine.draw_sprite( 'player', V2( 1, floor( self.image_walk ) % 8 ), self.pos.c().s( 0, ( 1 - PLAYER_HITBOX[1] ) / 2 ).m( GRID ), False, flip = V2( self.image_dir, 1 ) )

    # Checks if the player has a block immediately (to a limited degree) below them
    def is_on_block( self ):

        controller = self.engine.get_instance( 'controller' )
        for xx in range( floor( self.pos.x + ( 1 - PLAYER_HITBOX[0] ) / 2 + COLLISION_EPSILON ), ceil( self.pos.x + ( 1 + PLAYER_HITBOX[0] ) / 2 - COLLISION_EPSILON ) ):
            if ( controller.is_block( V2( xx, int( floor( self.pos.y + ( 1 + PLAYER_HITBOX[1] ) / 2 ) ) ) ) ):
                return True
        return False

    # Returns a list of the vectors of any blocks the player is inside of
    def get_adjacent_blocks( self, position = None ):

        if position == None:
            position = self.pos
        output = []

        bound_1 = position.c().a( V2( PLAYER_HITBOX ).c().m( -1 ).a( 1 ).d( 2 ) ).a( COLLISION_EPSILON )
        bound_2 = position.c().a( V2( PLAYER_HITBOX ).c().a( 1 ).d( 2 ) ).s( COLLISION_EPSILON )

        for xx in range( int( floor( bound_1.x ) ), int( ceil( bound_2.x ) ) ):
            for yy in range( int( floor( bound_1.y ) ), int( ceil( bound_2.y ) ) ):    
                output.append( V2( xx, yy ) )
        return output

    # Push the player out of any adjacent blocks
    def push_out( self, is_x_axis ):

        controller = self.engine.get_instance( 'controller' )
        adjacent_blocks = self.get_adjacent_blocks()

        # For every grid space the player is inside of
        for block_pos in adjacent_blocks:

            # Only continue if a block occupies this grid space
            if ( not controller.is_block( block_pos ) ):
                continue

            # Push the player out based on their position within the block
            # The is_x_axis argument determines the axis they're pushed along
            if ( is_x_axis ):
                direction = -1 if self.pos.x < block_pos.x else 1
                self.pos.x = block_pos.x + direction * ( 1 + PLAYER_HITBOX[0] ) / 2
                self.vel.x = 0
            else:
                direction = -1 if self.pos.y < block_pos.y else 1
                self.pos.y = block_pos.y + direction * ( 1 + PLAYER_HITBOX[1] ) / 2
                self.vel.y = 0

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
    def image_dir( self ):
        return self._image_dir

    @property
    def image_walk( self ):
        return self._image_walk

    @property
    def image_bob( self ):
        return self._image_bob