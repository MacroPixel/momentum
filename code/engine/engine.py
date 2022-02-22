import os
os.environ[ 'PYGAME_HIDE_SUPPORT_PROMPT' ] = ''
import pygame
from pygame.locals import RLEACCEL
from math import floor, ceil

from .game_object import *
from .vector import *

# Switching a room immediately unloads everything instead of
# waiting until the end of the update event
class RoomSwitch ( Exception ):

    def __init__( self, func ):

        self.func = func

# Abstracts most of the Pygame stuff away
class Engine:

    # Initially set up Pygame & specify global options
    def __init__( self, size, caption, room_dict, start_room, *args, **kwargs ):

        # Can't be changed for the time being
        self._screen_size = V2( size )

        # Create the window with the desired screen size
        pygame.init()
        pygame.display.set_caption( caption )
        self.__screen = pygame.display.set_mode( self.screen_size.l(), pygame.RESIZABLE )
        self.__clock = pygame.time.Clock()
        self.__fps_clock = pygame.time.Clock()

        # Set the root directory
        # This is where all game resources go, independent of game code
        self.__root_dir = self.dict_search( kwargs, 'root_dir', os.path.dirname( os.getcwd() ) )

        # Set the application icon
        if ( 'icon_source' in kwargs ):
            pygame.display.set_icon( pygame.image.load( self.get_path( kwargs[ 'icon_source' ] ) ) )

        # Remember the max FPS
        self.fps_limit = self.dict_search( kwargs, 'fps_limit', 0 )

        # All sprites are broken into subimages and stored in self.__sprites
        self.__sprites = {}
        self.reload_sprites()

        # All sound objects are stored in self.__sound_paths
        # 32 sounds can be played at once
        pygame.mixer.set_num_channels( 32 )
        self.__sounds = {}
        self.__music = {}
        self.reload_sounds()
        self._next_song = {}
        self.MUSIC_END = pygame.USEREVENT + 1

        # Holds a reference to every GameObject
        self.__instances = []
        self.__draw_instances = []
        self.__named_instances = {}
        self.__tagged_instances = {}

        # Initialize containers for keyboard/mouse inputs
        self.__keys_down = []
        self.__keys_up = []
        self.__keys = pygame.key.get_pressed()
        self.__mouse_buttons_down = []
        self.__mouse_buttons_up = []
        self.__mouse_buttons = pygame.mouse.get_pressed()

        # Other variables
        self._delta_time = 0
        self._view_pos = V2()
        self._view_zoom = self.dict_search( kwargs, 'zoom_level', V2( 1, 1 ) )
        self.__fonts = {}
        self.__bitmap_fonts = {}
        self.__zoom_buffer = {}

        # Goto a room
        # This is when the user's room code is used
        self.__room_dict = room_dict
        self.load_room( start_room )

    # Enter the main loop
    def run( self ):

        self.__is_running = True
        while self.__is_running:

            # Reset necessary variables
            self._delta_time = min( 0.1, self.__clock.tick() / 1000 )
            self.__keys_down = []
            self.__keys_up = []
            self.__keys = pygame.key.get_pressed()
            self.__mouse_buttons_down = []
            self.__mouse_buttons_up = []
            self.__mouse_buttons = pygame.mouse.get_pressed()

            # EVENTS
            for event in pygame.event.get():

                # Quit the game
                if event.type == pygame.QUIT:
                    self.__is_running = False

                # Resize the window
                if event.type == pygame.VIDEORESIZE:
                    self._screen_size = V2( event.size )

                # Log key/mouse inputs
                elif event.type == pygame.KEYDOWN:
                    self.__keys_down.append( event.key )
                elif event.type == pygame.KEYUP:
                    self.__keys_up.append( event.key )
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.__mouse_buttons_down.append( event.button )
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.__mouse_buttons_up.append( event.button )

                # Music queue
                elif event.type == self.MUSIC_END:
                    if 'name' in self._next_song:
                        self.play_music( self._next_song[ 'name' ], **self._next_song[ 'kwargs' ] )

            # Cancel updating/drawing if room is switched
            try:

                # update() is called once per frame for all GameObjects
                for obj in self.__instances:
                    obj.update()

                # After resetting the draw window, draw() can be called for all GameObjects
                self.__screen.fill( ( 0, 0, 0 ) )
                for obj in self.__draw_instances:
                    obj.draw()
                
                # Swap buffers
                pygame.display.update()

                # Limit FPS if necessary
                if ( self.fps_limit > 0 ):
                    self.__fps_clock.tick( self.fps_limit )

            except RoomSwitch as room:

                self.load_room( room.func )

    # Gets the state of a key (check of 0 = "is down", 1 = "was pressed", 2 = "was released")
    def get_key( self, key_id, check = 0 ):

        if check == 0:
            return self.__keys[ key_id ]
        elif check == 1:
            return key_id in self.__keys_down
        elif check == 2:
            return key_id in self.__keys_up

    # Gets the state of a key (check of 0 = "is down", 1 = "was pressed", 2 = "was released")
    def get_mouse_button( self, button_id, check = 0 ):

        if check == 0:
            return self.__mouse_buttons[ button_id ]
        elif check == 1:
            return button_id in self.__mouse_buttons_down
        elif check == 2:
            return button_id in self.__mouse_buttons_up

    # Appends the input to the root directory
    def get_path( self, directory ):

        return self.__root_dir + directory

    # Gets the position of the cursor within the world
    def get_world_cursor( self ):

        return self.to_world_coord( V2( pygame.mouse.get_pos() ) )

    # Loading a room clears all objects and runs a custom function
    # The function is stored in self.__room_dict under a string
    def load_room( self, room_function ):

        # Delete all objects (makes a copy of list so it can be altered during loop)
        for obj in self.__instances.copy():
            self.delete_instance( obj )

        # Executes inputted function
        self.__room_dict[ room_function ]( self )

    # Loading a room clears all objects and runs a custom function
    # The function is stored in self.__room_dict under a string
    def switch_room( self, room_function ):

        raise RoomSwitch( room_function )

    # Closes the game
    def close_app( self ):

        self.__is_running = False

    # GameObject-handling methods
    from ._engine_instances import add_instance
    from ._engine_instances import delete_instance
    from ._engine_instances import tag_instance
    from ._engine_instances import untag_instance
    from ._engine_instances import get_instance
    from ._engine_instances import get_instances
    from ._engine_instances import get_tagged_instance
    from ._engine_instances import get_tagged_instances

    # Drawing methods (preferred over pygame ones because they account for the game view)
    from ._engine_draw import reload_sprites
    from ._engine_draw import draw_line
    from ._engine_draw import draw_surface
    from ._engine_draw import draw_sprite
    from ._engine_draw import draw_text
    from ._engine_draw import draw_text_bitmap
    from ._engine_draw import to_screen_coord
    from ._engine_draw import to_world_coord
    from ._engine_draw import zoom_buffer_remove
    from ._engine_draw import get_sprite
    from ._engine_draw import create_font
    from ._engine_draw import create_bitmap_font

    # Sound methods
    from ._engine_mixer import reload_sounds
    from ._engine_mixer import play_sound
    from ._engine_mixer import play_music
    from ._engine_mixer import queue_music

    # Returns a value from a dictionary if found,
    # otherwise returns the default value passed into the function
    @staticmethod
    def dict_search( dictionary, key, default ):
        
        return dictionary[ key ] if key in dictionary else default

    # Getters and setters
    @property
    def screen_size( self ):
        return self._screen_size.c()

    @property
    def fps_limit( self ):
        return self._fps_limit

    @property
    def fps_current( self ):
        return self.__clock.get_fps()

    @fps_limit.setter
    def fps_limit( self, value ):

        value = int( value )
        if ( value < 0 ):
            raise ValueError( 'FPS limit must be 0 or positive' )
        else:
            self._fps_limit = value

    @property
    def delta_time( self ):
        return self._delta_time

    @property
    def view_pos( self ):
        return self._view_pos

    @view_pos.setter
    def view_pos( self, value ):
        self._view_pos = V2( value )

    @property
    def view_zoom( self ):
        return self._view_zoom.c()

    @view_zoom.setter
    def view_zoom( self, value ):

        # Clear the buffer containing the zoomed in surfaces
        if ( V2( value ) != self.view_zoom ):
            self.__zoom_buffer = {}

        # Change the zoom
        self._view_zoom = V2( value )

    @property
    def view_bound_min( self ):

        # Return the top-left of the visible screen in pixel non-screen coordinates
        return self.view_pos.c().s( self.screen_size.d( 2 ).d( self.view_zoom ) )

    @property
    def view_bound_max( self ):

        # Return the bottom-right of the visible screen in pixel non-screen coordinates
        return self.view_pos.c().a( self.screen_size.d( 2 ).d( self.view_zoom ) )