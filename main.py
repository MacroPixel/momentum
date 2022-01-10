import pygame
from math import floor, ceil, sin, cos
import random
from engine import *
from constants import *

class Controller( GameObject ):

  def __init__( self, engine ):

    super().create_instance()
    engine.create_font( 'res/misc/font_1.otf', 'main', 20 )
    engine.create_font( 'res/misc/font_1.otf', 'main', 12 )

    self.allow_debug = True
    self.debug = True

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

class UIController( GameObject ):

  def __init__( self ):

    super().create_instance( layer = -1000 )
    self.state = [ 1 ]

  def draw( self, engine ):

    if self.state[0] == 1:
      engine.draw_text( '[ESC] Pause', 'main:20', V2( 20, 20 ), ( 255, 255, 255 ) )

    if c_main.debug:
      engine.draw_text( 'Debug', 'main:12', engine.screen_size.c().s( 10, 10 ), ( 0, 100, 255 ), V2( 1, 1 ) )

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
      
  def draw( self, engine ):

    for coord in self.blocks:
      engine.draw_image( B_TEXTURES[ self.blocks[ coord ] ], V2( 0, 0 ), V2( *coord.split( ':' ) ).i().m( 32 ) )

  def set_block( self, pos, block_type ):

    pos = V2( pos )
    if block_type == B_NULL:
      self.blocks.pop( f'{ pos.x }:{ pos.y }' )
    else:
      self.blocks[ f'{ pos.x }:{ pos.y }' ] = block_type

  def get_block_type( self, pos ):

    return self.blocks[ f'{ pos.x }:{ pos.y }' ]

  def is_block( self, pos ):

    return f'{ pos.x }:{ pos.y }' in self.blocks

class Player ( GameObject ):

  def __init__( self ):

    super().create_instance( obj = 'player' )
    self.image = 0
    self.image_dir = 1
    self.pos = V2()
    self.vel = V2()

  def update( self, engine ):
    
    # Horizontal movement
    if engine.get_key( pygame.K_d ):
      self.vel.x += 600 * engine.delta_time
    elif engine.get_key( pygame.K_a ):
      self.vel.x -= 600 * engine.delta_time
    elif self.is_on_block():
      self.vel.x *= 0.02 ** engine.delta_time

    # Vertical movement
    if ( self.is_on_block() or c_main.debug ) and engine.get_key( pygame.K_SPACE ):
      self.vel.y = -600

    self.vel.y += 1000 * engine.delta_time

    # Actually move
    self.pos.a( self.vel.c().m( engine.delta_time ) )
    self.image += abs( self.vel.x ) * engine.delta_time / 10

    # Set image details
    if abs( self.vel.x ) < 15:
      self.image = 0
    if ( self.vel.x ) < -0.01:
      self.image_dir = -1
    elif ( self.vel.x > 0.01 ):
      self.image_dir = 1

    if engine.get_key( pygame.K_k ):
      self.delete()

    # Perform collision detection on the 4 adjacent blocks
    vel_factor = V2( 1, 1 )

    for xx in range( floor( self.pos.x / GRID ), ceil( self.pos.x / GRID ) + 1 ):
      for yy in range( floor( self.pos.y / GRID ), ceil( self.pos.y / GRID ) + 1 ):

        block_pos = V2( xx, yy )
        grid_vec = V2( GRID, GRID )

        if ( c_block.is_block( block_pos ) ):

          vector = collision_get( self.pos, block_pos.c().m( GRID ), grid_vec, grid_vec )
          self.pos.a( vector )
          if ( vector.x != 0 ):
            vel_factor.x = 0
          else:
            vel_factor.y = 0
            # print( vector.l() )

    self.vel.m( vel_factor )

  def draw( self, engine ):

    engine.draw_image_mod( 'player', V2( 1, floor( self.image ) % 8 ), self.pos, flip = V2( self.image_dir, 1 ) )

  def is_on_block( self ):

    return c_block.is_block( self.pos.c().a( 0, GRID + 0.001 ).d( GRID ).i() )

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