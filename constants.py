# Block IDs
B_NULL = 0
B_DEFAULT = 1
B_GOOP = 2
B_LEAF = 3
B_WOOD = 4
B_LAVA = 5
B_CLOUD = 6
B_TOTAL = 7

# Block textures (listed in order of ID)
B_TEXTURES = [
  None,
  'block_default',
  'block_goop',
  'block_leaf',
  'block_wood',
  'block_lava',
  'block_cloud'
]

# The color of each block when being loaded in from a PNG
B_COLORS = [
  None,
  ( 127, 127, 127, 255 ),
  ( 255, 127, 255, 255 ),
  ( 0, 0, 0, 255 ),
  ( 127, 63, 0, 255 ),
  ( 127, 0, 0, 255 ),
  ( 191, 255, 255, 255 )
]

# Determines how the sprite of a block type conencts
# to those of other blocks with the same type
BDM_DEF_OVERLAY = 0
BDM_DEF_REPLACE = 1
BDM_SINGLE_OVERLAY = 2

B_DRAW_MODES = [
  None,
  BDM_SINGLE_OVERLAY,
  BDM_DEF_REPLACE,
  BDM_DEF_OVERLAY,
  BDM_DEF_OVERLAY,
  BDM_DEF_OVERLAY,
  BDM_DEF_REPLACE
]

# The size of a block grid/chunk grid space
GRID = 32
C_GRID = 16

# How far the player has to go to the side of the screen
# for the view to scroll
VIEW_BOUNDS = ( 128, 64 )

# The maximum range (in block coords) beyond the screen
# within which the game should attempt to render blocks
RENDER_BOUNDS = ( 20, 20 )

# General physics constants
GRAVITY = 32

# Player movement constants
PLAYER_HSPEED = 10
PLAYER_HSPEED_BOOST = 3
PLAYER_FRICTION = 5000
PLAYER_JUMP_POWER = 18

PLAYER_HITBOX = ( 30 / 32, 28 / 30 )