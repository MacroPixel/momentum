import pygame
from math import floor, ceil, sin, cos
import random
from engine import *
from constants import *

# Controls basic game logic
# Other controller objects exist for more specific game logic
class Controller( GameObject ):

  def __init__( self, engine ):

    # Create fonts
    super().create_instance()
    engine.create_font( 'res/misc/font_1.otf', 'main', 20 )
    engine.create_font( 'res/misc/font_1.otf', 'main', 12 )

    # Debug mode can be toggled with right alt
    self.allow_debug = True
    self.debug = True

  # Mostly just debug stuff
  def update( self, engine ):

    # Switch debug mode if allowed
    if engine.get_key( pygame.K_RALT, 1 ):
      self.debug = not self.debug

    # Debug features
    if self.debug:
      
      # Restart
      if ( engine.get_key( pygame.K_r, 1 ) ):
        self.restart( self.get_instance( 'player' ) )

  # Reset the player & reload blocks
  def restart( self, player ):

    player.pos = V2( 0, 0 )
    player.vel = V2( 0, 0 )

# Handles UI drawing & responses
class UIController( GameObject ):

  def __init__( self ):

    # State represents the UI menu
    super().create_instance( layer = -1000 )
    self.state = [ 1 ]

  def draw( self, engine ):

    if self.state[0] == 1:
      engine.draw_text( '[ESC] Pause', 'main:20', V2( 20, 20 ), ( 255, 255, 255 ) )

    if c_main.debug:
      engine.draw_text( 'Debug', 'main:12', engine.screen_size.c().s( 10, 10 ), ( 0, 100, 255 ), V2( 1, 1 ) )

# Handles block storing/drawing
# Blocks aren't actually objects, they're only entries in an array
class BlockController( GameObject ):

  def __init__( self ):

    super().create_instance( layer = 0 )
    self.blocks = {}
    self.load_level()

  # Loads the level data into memory
  def load_level( self ):

    level_data = open( 'res/data/blocks.txt' ).read().split( '\n' )

    # Group the data into chunks (denoted by "* X:Y")
    # This is done solely to aid with drawing the blocks in
    self.chunks = {}
    self.loaded_chunks = []
    current_chunk = ''
    for line in level_data:

      # Switch chunk
      if line[0] == '*':
        current_chunk = line.split( '* ' )[1].split( ':' )
        try:
          current_chunk = f'{ int( current_chunk[0] ) }:{ int( current_chunk[1] ) }'
          self.chunks[ current_chunk ] = []
        except ( ValueError, IndexError ):
          raise GameError( 'Invalid chunk format' )

      # Create objects under chunk
      else:

        # Maps a string to an integer representing a block type
        enum_values = {
          'goop': B_GOOP
        }

        # If chunk isn't active
        if ( current_chunk == '' ):
          raise GameError( 'No chunk was specified' )

        # Otherwise, store the block name & loop through coordinates
        block_name = enum_values[ line.split( ' ' )[0] ]
        for i in range( 1, len( line.split( ' ' ) ), 2 ):

          # Create block & store position under current chunk
          temp_pos = V2( line.split( ' ' )[ i:i + 2 ] ).i().a( str_to_vec( current_chunk ).m( C_GRID ) )
          self.set_block( temp_pos, block_name )
          self.chunks[ current_chunk ].append( vec_to_str( temp_pos ) )

  # Creates a surface for easy-drawing
  # I've decided to postpone implementing this until there's enough blocks for it to make a difference
  def reload_chunks( self, player_pos ):
    pass
      
  # Iterate through/draw all blocks
  # May need to be redesigned later on for better performance
  def draw( self, engine ):

    for coord in self.blocks:
      engine.draw_image( B_TEXTURES[ self.blocks[ coord ] ], V2( 0, 0 ), str_to_vec( coord ).m( 32 ) )

  # Either changes a block or removes it (by setting it to B_NULL)
  def set_block( self, pos, block_type ):

    # Convert position & alter array
    pos = V2( pos )
    if block_type == B_NULL:
      self.blocks.pop( f'{ pos.x }:{ pos.y }' )
    else:
      self.blocks[ f'{ pos.x }:{ pos.y }' ] = block_type

  # Check whether a block exists at a position
  def is_block( self, pos ):

    return f'{ pos.x }:{ pos.y }' in self.blocks

  # Get the block type of a position
  # !!! WILL throw error if there isn't a block there
  def get_block_type( self, pos ):

    return self.blocks[ f'{ pos.x }:{ pos.y }' ]

# It's you :D
class Player ( GameObject ):

  def __init__( self ):

    # Store image & physics details
    super().create_instance( obj = 'player' )
    self.image_dir = 1
    self.image_walk = 0
    self.image_bob = 0
    self.pos = V2()
    self.vel = V2()

  def update( self, engine ):
    
    # Horizontal movement
    if engine.get_key( pygame.K_d ):
      self.vel.x += 18 * engine.delta_time
    elif engine.get_key( pygame.K_a ):
      self.vel.x -= 18 * engine.delta_time
    elif self.is_on_block():
      self.vel.x *= 0.02 ** engine.delta_time

    # Vertical movement
    if ( self.is_on_block() or c_main.debug ) and engine.get_key( pygame.K_SPACE ):
      self.vel.y = -18
    self.vel.y += 32 * engine.delta_time

    self.image_walk += abs( self.vel.x ) * engine.delta_time * 3

    # Set image details
    # Walk is incremented while velocity >= 0.2, otherwise head bob is incremented
    if abs( self.vel.x ) < 0.5:
      self.image_walk = 0
    if abs( self.vel.x ) < 0.5 and self.is_on_block():
      self.image_bob += engine.delta_time * 0.8
    else:
      self.image_bob = 0
    if ( self.vel.x ) < -0.01:
      self.image_dir = -1
    elif ( self.vel.x > 0.01 ):
      self.image_dir = 1

    if engine.get_key( pygame.K_k ):
      self.delete()

    # Actually move
    # Perform collision detection on the 4 adjacent blocks
    # This is done with multiple iterations to make it more precise
    vel_factor = V2( 1, 1 )

    iterations = 5
    for i in range( iterations ):

      self.pos.a( self.vel.c().m( engine.delta_time ).d( iterations ) )

      # Loop through adjacent blocks
      for block_pos in self.get_adjacent_blocks():

        # Skip this position if there's no block there
        if ( not c_block.is_block( block_pos ) ):
          continue

        # Store whether the block was an x-axis or y-axis collision
        # This is detemined based off of whether the player is inside a block
        # after their x-axis movement
        is_x_axis = False
        for alt_block_pos in self.get_adjacent_blocks( self.pos.c().s( 0, self.vel.y * engine.delta_time / iterations ) ):
          if c_block.is_block( alt_block_pos ):
            is_x_axis = True

        overlap = collision_get( self.pos, block_pos, V2( 1, 1 ), V2( 1, 1 ) )

        if ( is_x_axis ):
          vel_factor.x = 0
          self.pos.x += overlap.x
        else:
          vel_factor.y = 0
          self.pos.y += overlap.y

    self.vel.m( vel_factor )

  # Draw self at current position
  # Leverages flip operations & sub-images
  def draw( self, engine ):

    if abs( self.vel.x ) < 0.5:
      engine.draw_image_mod( 'player', V2( 0, floor( self.image_bob ) % 2 ), self.pos.c().m( GRID ), flip = V2( self.image_dir, 1 ) )
    else:
      engine.draw_image_mod( 'player', V2( 1, floor( self.image_walk ) % 8 ), self.pos.c().m( GRID ), flip = V2( self.image_dir, 1 ) )

  # Checks if the player has a block immediately (to a limited degree) below them
  def is_on_block( self ):

    return c_block.is_block( self.pos.c().a( 0, 1.001 ).i() ) or c_block.is_block( self.pos.c().a( 1, 1.001 ).i() )

  # Returns a list of the vectors of any blocks the player is inside of
  def get_adjacent_blocks( self, position = None ):

    if position == None:
      position = self.pos
    output = []
    for xx in range( floor( position.x ), ceil( position.x ) + 1 ):
      for yy in range( floor( position.y ), ceil( position.y ) + 1 ):    
        output.append( V2( xx, yy ) )
    return output

# Vector / string transformation
def vec_to_str( value ):
  return ':'.join( value.fn( lambda a: str( a ) ).l() )

def str_to_vec( value ):
  return V2( value.split( ':' ) ).i()

# I know global objects are considered bad practice, but I don't really care.
g_engine = Engine( V2( 1280, 720 ), 'My Game!' )
c_main = Controller( g_engine )
c_ui = UIController()
c_block = BlockController()

Player()

g_engine.run()