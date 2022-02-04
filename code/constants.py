import os
from pygame.locals import *

# Block IDs
B_NULL = 0
B_DEFAULT = 1
B_GOOP = 2
B_LEAF = 3
B_WOOD = 4
B_LAVA = 5
B_CLOUD = 6
B_BOUNCE = 7
B_SPRING = 8
B_TOTAL = 9

# Block textures (listed in order of ID)
B_TEXTURES = [
    None,
    'block_default',
    'block_goop',
    'block_leaf',
    'block_wood',
    'block_lava',
    'block_cloud',
    'block_bounce',
    'block_spring'
]

# The color of each block when being loaded in from a PNG
B_COLORS = [
    None,
    ( 127, 127, 127, 255 ),
    ( 255, 127, 255, 255 ),
    ( 0, 0, 0, 255 ),
    ( 127, 63, 0, 255 ),
    ( 127, 0, 0, 255 ),
    ( 191, 255, 255, 255 ),
    ( 255, 0, 255, 255 ),
    ( 127, 255, 127, 255 )
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
    BDM_DEF_REPLACE,
    BDM_SINGLE_OVERLAY,
    BDM_SINGLE_OVERLAY
]

# Internal names of each block
B_STRINGS = [
    None,
    'default',
    'goop',
    'leaf',
    'wood',
    'lava',
    'cloud',
    'bounce',
    'spring'
]

# Blocks that cause bouncing
B_BOUNCE = [
    'bounce'
]
BOUNCE_FACTOR = 0.7

# The size of a block grid/chunk grid space
GRID = 16
C_GRID = 16

# How far the player has to go to the side of the screen
# for the view to scroll
VIEW_BOUNDS = ( 128, 64 )

# The maximum range (in block coords) away from the center
# within which the game should attempt to render blocks
RENDER_BOUNDS = ( 2, 2 )

# General physics constants
GRAVITY = 32

# Player movement constants
PLAYER_HSPEED = 18
PLAYER_HSPEED_AIR_FACTOR = 0.2
PLAYER_HSPEED_BOOST = 1
PLAYER_HSPEED_ATTACK_FACTOR = 0.4
PLAYER_FRICTION = 20000
PLAYER_JUMP_POWER = 19

PLAYER_HITBOX = ( 44 / 48, 44 / 48 )
COLLISION_EPSILON = 0.000001

# Keybinds (will probably be moved to settings object in the future)
BINDS = {
    'move_left': K_a,
    'move_right': K_d,
    'jump': K_SPACE,
    'attack': K_k,
    'invert': K_i
}

# Used by controller's pause_level variable
PAUSE_NONE = 0
PAUSE_NORMAL = 1
PAUSE_TOTAL = 2