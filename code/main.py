import pygame
from math import floor, ceil, sin, cos
import random
from engine import *
from constants import *

class Controller( GameObject ):

  def __init__( self, engine ):

    super().create_instance()
    engine.create_font( 'res/misc/font_1.otf', 'main', 20 )

class UIController( GameObject ):

  def __init__( self ):

    super().create_instance( layer = 1000 )
    self.state = [ 1 ]

  def draw( self, engine ):

    if self.state[0] == 1:
      engine.draw_text( '[ESC] Pause', 'main:20', V2( 20, 20 ), ( 255, 255, 255 ) )

class BlockController( GameObject ):

  def __init__( self ):

    super().create_instance( layer = 0 )
    self.blocks = {}

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
    self.pos = V2()
    self.vel = V2()

  def update( self, engine ):
    
    # Horizontal movement
    if engine.get_key( pygame.K_d ):
      self.vel.x += 600 * engine.delta_time
    elif engine.get_key( pygame.K_a ):
      self.vel.x -= 600 * engine.delta_time

    # Vertical movement
    if engine.get_key( pygame.K_SPACE, 1 ):
      self.vel.y = -600

    self.vel.y += 1000 * engine.delta_time
    self.pos.a( self.vel.c().m( engine.delta_time ) )

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
            vel_factor.y = -0.5

    self.vel.m( vel_factor )

  def draw( self, engine ):

    engine.draw_image( 'player', V2( 0, 0 ), self.pos )

g_engine = Engine( ( 1280, 720 ), 'My Game!' )

c_main = Controller( g_engine )
c_ui = UIController()
c_block = BlockController()

Player()

c_block.set_block( V2( 2, 2 ), B_LEAF )
for i in range( 10 ):
  c_block.set_block( V2( i, 10 ), B_GOOP )

g_engine.run()