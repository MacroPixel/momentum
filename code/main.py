import pygame
from math import floor, ceil, sin, cos
import random
import os

from player import *
from controller import *

from engine import *
from constants import *

# I know global objects are considered bad practice, but I don't really care.
g_engine = Engine( V2( 1280, 720 ), 'Untitled Platformer',
    root_dir = os.path.dirname( os.getcwd() ) + '/res',
    icon_source = '/textures/icon.png',
    fps_limit = 0
)

Controller( g_engine )
Player( g_engine )

g_engine.run()