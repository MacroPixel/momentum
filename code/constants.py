import os
from pygame.locals import *

# Layers for draw order
# Smaller layer = further back
LAYER_BACKGROUND = 0
LAYER_BLOCK = 1
LAYER_ENTITY = 2
LAYER_PLAYER = 3
LAYER_PARTICLE = 4
LAYER_RAGDOLL = 5
LAYER_UI = 6

# Internal names of each block
# Every other block array uses the order of this list
# They cannot share the name of an entity
B_STRINGS = [
    'default',
    'goop',
    'leaf',
    'wood',
    'lava',
    'cloud',
    'bounce',
    'bounce_extra',
    'spring',
    'spikes',
    'metal',
    'metal_alt',
    'sand',
    'water'
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
    'block_bounce_extra',
    'block_spring',
    'block_spikes',
    'block_metal',
    'block_metal_alt',
    'block_sand',
    'block_water'
]

# The color of each block when being loaded in from a PNG
B_COLORS = [
    '7f7f7f',
    'ff7fff',
    'dbf87a',
    '7f3f00',
    '7f0000',
    'bfffff',
    'ff00ff',
    '6300ff',
    '7fff7f',
    'ff7f7f',
    '764d47',
    '4d3b39',
    'f3d681',
    '3ccff3'
]

# Determines how the sprite of a block type conencts
# to those of other blocks with the same type
BDM_NORMAL = 0
BDM_OVERLAY = 1
BDM_REPLACE = 2

B_DRAW_MODES = [
    BDM_OVERLAY,
    BDM_REPLACE,
    BDM_NORMAL,
    BDM_OVERLAY,
    BDM_OVERLAY,
    BDM_REPLACE,
    BDM_REPLACE,
    BDM_REPLACE,
    BDM_OVERLAY,
    BDM_REPLACE,
    BDM_REPLACE,
    BDM_OVERLAY,
    BDM_REPLACE,
    BDM_REPLACE
]

B_DRAW_VARIANTS = [
    1,
    5,
    4,
    3,
    3,
    3,
    1,
    1,
    1,
    1,
    1,
    1,
    3,
    3
]

# List of blocks that don't connect to blocks of different types
B_NO_CONNECT = [
    'spikes',
    'goop',
    'bounce',
    'water'
]

# List of blocks that entities can go through
B_PASSABLE = [
    'spikes',
    'water'
]

# List of blocks that refresh jump when inside of
B_FLUID = [
    'water'
]

# Keys are blocks that allow bouncing
# Values are the bounce factor
B_BOUNCE = {
    'bounce': 0.7,
    'bounce_extra': 1.2
}

# List of blocks that kill entities
B_HAZARD = [
    'spikes'
]

# Internal names of each entity
# Every other block array uses the order of this list
# They cannot share the name of an entity
ENTITY_STRINGS = [
    'jomper',
    'zeedle',
    'flooter',
    'checkpoint',
    'hook',
    'box',
    'powerup',
    'twig',
    'launcher',
    'saw'
]

# The color of each entity when being loaded in from a PNG
ENTITY_COLORS = [
    'ff3fff',
    'ffbc8b',
    'fff94f',
    '3fffbf',
    'bfbfbf',
    'a46a4a',
    'ff9f7f',
    'a06642',
    '93f0b0',
    '6e6e6e'
]

# A string representation of each entity class
ENTITY_CLASSES = [
    'Jomper',
    'Zeedle',
    'Flooter',
    'Checkpoint',
    'Rope_Hook',
    'Box',
    'Powerup',
    'Twig',
    'Launcher',
    'Saw'
]

# Object arrays use the block and entity arrays
# The blocks are listed first, and then the enemies

# Internal names of each object
O_STRINGS = B_STRINGS + ENTITY_STRINGS

# The color of each object when being loaded in from a PNG
# Allows the colors of other special objects that don't
# fall into either category (e.g. checkpoints)
O_COLORS = B_COLORS + ENTITY_COLORS

# Internal names of each region
# Regions define the background/music for an region
REGION_STRINGS = [
    'tutorial',
    'purple',
    'steampunk',
    'ocean',
    'forest'
]

# The blocks that trigger each region
REGION_BLOCKS = [
    [ 'default' ],
    [ 'goop' ],
    [ 'metal', 'metal_alt' ],
    [ 'sand' ],
    [ 'leaf' ]
]

# Lists the music to be played in each region
REGION_SONGS = [
    'mus_tutorial',
    'mus_purple',
    'mus_steampunk',
    'mus_ocean',
    'mus_forest'
]

# Defines a background for each region (listed in the same order)
# Like ENTITY_CLASSES, it stores the literal name of the class
# to be eval()'d when instances of it are created
REGION_BGS = [
    'Background_Region_1',
    'Background_Region_2',
    'Background_Region_3',
    'Background_Region_4',
    'Background_Region_5'
]

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
RENDER_BOUNDS = ( 1, 1 )

# Entity physics constants
GRAVITY = 32
ENTITY_MAX_VEL = 150

# Player movement constants
PLAYER_HSPEED = 22
PLAYER_HSPEED_AIR_FACTOR = 0.2
PLAYER_HSPEED_BOOST = 3
PLAYER_HSPEED_ATTACK_FACTOR = 0.4
PLAYER_FRICTION = 20000
PLAYER_JUMP_POWER = 19
PLAYER_SWIM_POWER = 12
PLAYER_MIN_WALL_VEL = 8
PLAYER_MAX_WALL_VEL = 25

COLLISION_EPSILON = 0.000001

# String representation of each ability
# Abilities are usually referenced using their strings,
# unlike objects, which are referenced using their numeric IDs
ABILITY_STRINGS = [
    'invert',
    'wall_jump',
    'stomp',
    'teleport',
    'slot',
    'rope',
    'glide'
]

# The block that a powerup should use to resolve which
# ability it referrs to
ABILITY_BLOCKS = [
    'goop',
    'metal_alt',
    'sand',
    'goop',
    'goop',
    'goop',
    'goop'
]

# Internal name for each item
# The name that's actually shown to the player
# is in a different dictionary
ITEM_STRINGS = [
    'box'
]

# Item names that are actually displayed to the player
ITEM_NAMES = [
    'Box'
]

# The entities that are created when items are dropped
# Use the internal names of the entity
ITEM_ENTITIES = [
    'box'
]

# Keybinds (will probably be moved to settings object in the future)
BINDS = {
    'move_left': K_a,
    'move_right': K_d,
    'jump': K_SPACE,
    'up_action': K_UP,
    'down_action': K_DOWN,
    'left_action': K_LEFT,
    'right_action': K_RIGHT
}
MUS_VOLUME = 0.5

# Used by controller's pause_level variable
PAUSE_NONE = 0
PAUSE_NORMAL = 1
PAUSE_TOTAL = 2