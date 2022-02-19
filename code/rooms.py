from basic_imports import *
from controller import *
from player import *
from menu_controller import *
from splash import *

# MAIN ROOM
# Needs a controller and player object
# Both of those objects control the whole level
def room_main( engine ):

    Controller( engine )

# MENU ROOM
# Where the game starts
# Allows going to other rooms
def room_frontend( engine ):

    Menu_Controller( engine )

# SPLASH ROOM
# Shows when the game first loads
def room_splash( engine ):

    Splash( engine )

# Defines each room with a string
ROOM_DICT = {
    'frontend': room_frontend,
    'main': room_main,
    'splash': room_splash
}