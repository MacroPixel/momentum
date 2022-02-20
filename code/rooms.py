from basic_imports import *
from controller import *
from player import *
from frontend_controller import *
from menu_controller import *
from splash import *

# MAIN ROOM
# Needs a controller and player object
# Both of those objects control the whole level
def room_main( engine ):

    Controller( engine )

# FRONTEND ROOM
# Where the game starts
def room_frontend( engine ):

    Frontend_Controller( engine )

# MENU ROOM
# Allows access to settings, etc.
def room_menu( engine ):

    Menu_Controller( engine )

# SPLASH ROOM
# Shows when the game first loads
def room_splash( engine ):

    Splash( engine )

# Defines each room with a string
ROOM_DICT = {
    'frontend': room_frontend,
    'menu': room_menu,
    'main': room_main,
    'splash': room_splash
}