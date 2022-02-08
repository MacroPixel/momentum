import os
from pygame.locals import *

# Layers for draw order
# Smaller layer = further back
LAYER_BLOCK = 0
LAYER_ENTITY = 1
LAYER_RAGDOLL = 2
LAYER_UI = 3

# Internal names of each block
# Every other block array uses the order of this list
# They cannot share the name of an enemy
B_STRINGS = [
    'default',
    'goop',
    'leaf',
    'wood',
    'lava',
    'cloud',
    'bounce',
    'spring',
    'spikes'
]

# Block textures (listed in order of ID)
B_TEXTURES = [
    'block_default',
    'block_goop',
    'block_leaf',
    'block_wood',
    'block_lava',
    'block_cloud',
    'block_bounce',
    'block_spring',
    'block_saw'
]

# The color of each block when being loaded in from a PNG
B_COLORS = [
    ( 127, 127, 127, 255 ),
    ( 255, 127, 255, 255 ),
    ( 0, 0, 0, 255 ),
    ( 127, 63, 0, 255 ),
    ( 127, 0, 0, 255 ),
    ( 191, 255, 255, 255 ),
    ( 255, 0, 255, 255 ),
    ( 127, 255, 127, 255 ),
    ( 255, 127, 127, 255 )
]

# Determines how the sprite of a block type conencts
# to those of other blocks with the same type
BDM_SINGLE = 0
BDM_SINGLE_OVERLAY = 1
BDM_3VAR_OVERLAY = 2
BDM_3VAR_REPLACE = 3

B_DRAW_MODES = [
    BDM_SINGLE_OVERLAY,
    BDM_3VAR_REPLACE,
    BDM_3VAR_OVERLAY,
    BDM_3VAR_OVERLAY,
    BDM_3VAR_OVERLAY,
    BDM_3VAR_REPLACE,
    BDM_SINGLE_OVERLAY,
    BDM_SINGLE_OVERLAY,
    BDM_SINGLE
]

# List of blocks that don't connect to blocks of different types
B_NO_CONNECT = [
    'spikes'
]

# List of blocks that entities can go through
B_PASSABLE = [
    'spikes'
]

# Keys are blocks that allow bouncing
# Values are the bounce factor
B_BOUNCE = {
    'bounce': 0.7
}

# List of blocks that kill entities
B_HAZARD = [
    'spikes'
]

# Internal names of each enemy
# Every other block array uses the order of this list
# They cannot share the name of an enemy
ENEMY_STRINGS = [
    'jomper'
]

# The color of each enemy when being loaded in from a PNG
ENEMY_COLORS = [
    ( 255, 63, 255 )
]

# A string representation of each enemy class
ENEMY_CLASSES = [
    'Jomper'
]

# Object arrays use the block and enemy arrays
# The blocks are listed first, and then the enemies

# Internal names of each object
O_STRINGS = B_STRINGS + ENEMY_STRINGS

# The color of each object when being loaded in from a PNG
# Allows the colors of other special objects that don't
# fall into either category (e.g. checkpoints)
O_COLORS = B_COLORS + ENEMY_COLORS
O_COLOR_CHECKPOINT = ( 63, 255, 191 )

# Different UI levels
UI_LEVEL = 0
UI_PAUSE = 1
UI_DEAD = 2

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
PLAYER_HSPEED_BOOST = 3
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