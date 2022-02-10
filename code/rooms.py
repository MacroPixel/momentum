from basic_imports import *
from controller import *
from player import *
from menu_controller import *
from background_container import *

# MAIN ROOM
# Needs a controller and player object
# Both of those objects control the whole level
def room_main( engine ):

    Controller( engine )
    Player( engine )
    Background_Container()

# MENU ROOM
# Where the game starts
# Allows going to other rooms
def room_frontend( engine ):

    Menu_Controller( engine )

# Defines each room with a string
ROOM_DICT = {
    'frontend': room_frontend,
    'main': room_main
}