# I put "engine" in very heavy quotes since this is a paper-thin abstraction
# over normal python code, but I also don't know what else to call it

import pygame
from pygame.locals import RLEACCEL

# An Object that receives update() and draw() events
class GameObject:

  # Holds a reference to every GameObject
  instances = []
  draw_instances = []
  named_instances = {}
  engine = None

  # Do other setup
  def create_instance( self, obj = '', layer = 0 ):

    self.layer = layer

    self.instances.append( self )

    self.obj = obj
    if self.obj != '':

      if self.obj not in self.named_instances:
        self.named_instances[ self.obj ] = []
      self.named_instances[ self.obj ].append( self )

    i = 0
    for i in range( len( self.draw_instances ) ):
      if self.draw_instances[i].layer < self.layer:
        break
    
    self.draw_instances.insert( i, self )

  # Remove from lists
  def delete( self ):

    self.instances.remove( self )
    self.draw_instances.remove( self )
    
    if self.obj != '':
      self.named_instances[ self.obj ].remove( self )

  # Called once a frame
  def update( self, engine ):
    pass

  # Called 10 times a second (for performance reasons)
  def tick( self, engine ):
    pass

  # Draws stuff to the screen
  def draw( self, engine ):
    pass

  # Returns one or multiple instances of a type
  def get_instance( self, instance_id ):

    if ( instance_id not in self.named_instances or len( self.named_instances[ instance_id ] ) == 0 ):
      return None
    return self.named_instances[ instance_id ][0]

  def get_instances( self, instance_id ):

    if ( instance_id not in self.named_instances or len( self.named_instances[ instance_id ] ) == 0 ):
      return None
    return self.named_instances[ instance_id ]

# A more specialized GameObject designed for displaying a sprite
class SpriteObject ( GameObject ):

  # Create a sprite/position variable in addition to the normal setup
  def create_instance( self, sprite_surf, coords ):

    super().create_instance()
    self.sprite = sprite_surf
    self.pos = V2( coords )

  # Automatically draw the sprite
  def draw( self, engine ):

    engine.screen.blit( self.sprite, self.pos.l() )

# Abstracts most of the Pygame stuff away
class Engine:

  # Initially set up Pygame & specify global options
  def __init__( self, size, caption ):

    GameObject.engine = self

    self.screen_size = size

    pygame.init()
    pygame.display.set_caption( caption )

    self.screen = pygame.display.set_mode( self.screen_size )
    self.clock = pygame.time.Clock()

    # All sprites are loaded into a dictoinary
    self.images = {}
    self.sprites = {}
    spr_file = open( 'res/textures/list.txt' ).read().split( '\n' )

    for line in spr_file:

      line = line.split( ' = ' )
      surface = pygame.image.load( 'res/textures/' + line[1].split( ' ' )[0] )
      surface = pygame.transform.scale( surface, V2( surface.get_size() ).m( int( line[1].split( ' ' )[1].split( ':' )[0] ) ).l() )
      self.sprites[ line[0] ] = surface

      dims = V2( surface.get_size() )
      square_count = V2( int( line[1].split( ' ' )[1].split( ':' )[1] ), int( line[1].split( ' ' )[1].split( ':' )[2] ) )
      square_size = dims.c().d( square_count )

      self.images[ line[0] ] = [ [ surface.subsurface( ( xx * square_size.x, yy * square_size.y, *square_size.l() ) ) for xx in range( square_count.x ) ]
        for yy in range( square_count.y ) ]

    # Other variables
    self.delta_time = 0
    self.keys_down = []
    self.keys_up = []
    self.keys = pygame.key.get_pressed()
    self.fonts = {}

  # Enter the main loop (called privately from constructor)
  def run( self ):

    running = True
    while running:

      # Reset necessary variables
      self.delta_time = min( 0.1, self.clock.tick() / 1000 )
      self.keys = pygame.key.get_pressed()
      self.keys_down = []
      self.keys_up = []

      for event in pygame.event.get():

        # Quit the game
        if event.type == pygame.QUIT:
          running = False

        # Log keypresses
        elif event.type == pygame.KEYDOWN:
          self.keys_down.append( event.key )

        elif event.type == pygame.KEYUP:
          self.keys_up.append( event.key )

      # update() is called once per frame for all GameObjects
      for obj in GameObject.instances:
        obj.update( self )

      # tick() is called 10 times a second for all GameObjects

      # After resetting the draw window, draw() can be called for all GameObjects
      self.screen.fill( ( 0, 0, 0 ) )

      for obj in GameObject.draw_instances:
        obj.draw( self )
      
      pygame.display.flip()

  # Shortcut for blitting surface onto screen
  def draw_image( self, sprite_id, frame, pos ):

    self.screen.blit( self.images[ sprite_id ][ frame.x ][ frame.y ], pos.l() )

  # Gets the state of a key (check of 0 = "is down", 1 = "was pressed", 2 = "was released")
  def get_key( self, key_id, check = 0 ):

    if check == 0:
      return self.keys[ key_id ]
    elif check == 1:
      return key_id in self.keys_down
    elif check == 2:
      return key_id in self.keys_up

  def create_font( self, filepath, name, size ):

    self.fonts[ f'{ name }:{ size }' ] = pygame.font.Font( filepath, size )

  def draw_text( self, text, font, pos, color ):

    self.screen.blit( self.fonts[ font ].render( text, True, color ), V2( pos ).l() )

# Compact vector class
class V2:

  def __init__( self, a = 0, b = 0 ):

    if isinstance( a, V2 ):
      self.u( a.x, a.y )
    elif type( a ) == list or type( a ) == tuple:
      self.u( a[0], a[1] )
    else:
      self.u( a, b )

  # These two functions help to reduce repetitive code within the operation functions
  def __op( self, a, b, op ):

    if op == '+': return a + b
    elif op == '-': return a - b
    elif op == '*': return a * b
    elif op == '/': return a / b
    elif op == 'fn': return b( a )

  def __op2( self, a, b, op ):

    if isinstance( a, V2 ):
      self.x = self.__op( self.x, a.x, op )
      self.y = self.__op( self.y, a.y, op )
    elif type( a ) == list or type( a ) == tuple:
      self.x = self.__op( self.x, a[0], op )
      self.y = self.__op( self.y, a[1], op )
    else:
      self.x = self.__op( self.x, a, op )
      self.y = self.__op( self.y, a if b == 'd' else b, op )

  # Update
  def u( self, a = 0, b = 0 ):

    self.x = a
    self.y = b
    return self

  # Add
  def a( self, a, b = 'd' ):
    self.__op2( a, b, '+' )
    return self

  # Subtract
  def s( self, a, b = 'd' ):
    self.__op2( a, b, '-' )
    return self

  # Multiply
  def m( self, a, b = 'd' ):
    self.__op2( a, b, '*' )
    return self

  # Divide
  def d( self, a, b = 'd' ):
    self.__op2( a, b, '/' )
    return self

  # Custom function
  def fn( self, a, b = 'd' ):
    self.__op2( a, b, 'fn' )
    return self
    
  # Return a list
  def l( self ):
    return [ self.x, self.y ]

  # Cast to int
  def i( self ):

    self.x = int( self.x )
    self.y = int( self.y )
    return self

  # Return a copy
  def c( self ):
    c = V2( self.x, self.y )
    return c

# Checks for a collision between two rectangles defined by their position and dimensions (using AABB, of course)
def collision_check( pos1, pos2, dim1, dim2 ):

  return ( pos1.x < pos2.x + dim2.x and pos2.x < pos1.x + dim1.x ) and ( pos1.y < pos2.y + dim2.y and pos2.y < pos1.y + dim1.y )

# Gets the push vector from a collision, assuming the first object is dynamic
def collision_get( pos1, pos2, dim1, dim2 ):

  overlap = V2( ( dim1.x + dim2.x ) * 0.5 - abs( pos1.x - pos2.x ), ( dim1.y + dim2.y ) * 0.5 - abs( pos1.y - pos2.y ) )

  if overlap.x < overlap.y:
    overlap.m( -1 if pos1.x < pos2.x else 1, 0 )
  else:
    overlap.m( 0, -1 if pos1.y < pos2.y else 1 )

  return overlap