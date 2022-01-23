# I put "engine" in very heavy quotes since this is a paper-thin abstraction
# over normal python code, but I also don't know what else to call it

import pygame
from pygame.locals import RLEACCEL
import os

from vector import *
from game_object import *

# Abstracts most of the Pygame stuff away
class Engine:

    # Initially set up Pygame & specify global options
    # def __init__( self, size, caption, icon_source = None, fps_limit = -1, root_dir = '' ):
    def __init__( self, size, caption, *args, **kwargs ):

        # Can't be changed for the time being
        self._screen_size = V2( size )

        # Create the window with the desired screen size
        pygame.init()
        pygame.display.set_caption( caption )
        self.__screen = pygame.display.set_mode( self.screen_size.l() )
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
        self.__load_sprites()

        # Holds a reference to every GameObject
        self.__instances = []
        self.__draw_instances = []
        self.__named_instances = {}

        # Other variables
        self._delta_time = 0
        self._view_pos = V2()
        self._view_size = V2( 1, 1 )
        self.__keys_down = []
        self.__keys_up = []
        self.__keys = pygame.key.get_pressed()
        self.__fonts = {}

    # Enter the main loop
    def run( self ):

        running = True
        while running:

            # Reset necessary variables
            self._delta_time = min( 0.1, self.__clock.tick() / 1000 )
            self.__keys = pygame.key.get_pressed()
            self.__keys_down = []
            self.__keys_up = []

            # EVENTS
            for event in pygame.event.get():

                # Quit the game
                if event.type == pygame.QUIT:
                    running = False

                # Log keypresses
                elif event.type == pygame.KEYDOWN:
                    self.__keys_down.append( event.key )
                elif event.type == pygame.KEYUP:
                    self.__keys_up.append( event.key )

            # update() is called once per frame for all GameObjects
            for obj in self.__instances:
                obj.update()

            # tick() is called 10 times a second for all GameObjects

            # After resetting the draw window, draw() can be called for all GameObjects
            self.__screen.fill( ( 21, 21, 21 ) )
            for obj in self.__draw_instances:
                obj.draw()
            
            # Swap buffers
            pygame.display.flip()

            # Limit FPS if necessary
            if ( self.fps_limit > 0 ):
                self.fps_clock.tick( self.fps_limit )

    # Stores a GameObject for later usage
    def add_instance( self, game_object ):

        # "instances" holds every active GameObject
        self.__instances.append( game_object )

        # "named_instances" allows searching for an object by name
        if game_object.object_id not in self.__named_instances:
            self.__named_instances[ game_object.object_id ] = []
        self.__named_instances[ game_object.object_id ].append( game_object )

        # Insert into proper draw-order-position based on layer
        i = 0
        for i in range( len( self.__draw_instances ) ):
            if self.__draw_instances[i].layer < game_object.layer:
                break
        self.__draw_instances.insert( i, game_object )

    # Removes a GameObject from memory
    def delete_instance( self, game_object ):

        self.__instances.remove( game_object )
        self.__draw_instances.remove( game_object )
        self.__named_instances[ game_object.object_id ].remove( game_object )

    # Gets the state of a key (check of 0 = "is down", 1 = "was pressed", 2 = "was released")
    def get_key( self, key_id, check = 0 ):

        if check == 0:
            return self.__keys[ key_id ]
        elif check == 1:
            return key_id in self.__keys_down
        elif check == 2:
            return key_id in self.__keys_up

    # Returns a sprite surface for other objects to use
    def get_sprite( self, sprite_id, frame ):

        return self.__sprites[ sprite_id ][ frame.x ][ frame.y ]

    # Shortcut for blitting surface onto screen
    def draw_surface( self, surf, pos ):

        self.__screen.blit( surf, pos.s( self._view_pos ).l() )

    # Uses pre-defined sprite
    def draw_sprite( self, sprite_id, frame, pos ):

        self.draw_surface( self.__sprites[ sprite_id ][ frame.x ][ frame.y ], pos )

    # Shortcut for blitting transformed surface onto screen
    def draw_surface_mod( self, surf, pos, scale = None, flip = None ):

        # Check each transformation argument to see if sprite needs to be modified
        if ( scale != None ):
            surf = pygame.transform.scale( surf, V2( surf.get_size() ).m( scale ).l() )
        if ( flip != None ):
            surf = pygame.transform.flip( surf, flip.x == -1, flip.y == -1 )

        # Draw the modified surface
        self.__screen.blit( surf, pos.s( self._view_pos ).l() )

    # Uses pre-defined surface
    def draw_sprite_mod( self, sprite_id, frame, pos, scale = None, flip = None ):

        self.draw_surface_mod( self.__sprites[ sprite_id ][ frame.x ][ frame.y ], pos, scale, flip )

    # Creates a font under the name 'name:size'
    def create_font( self, filepath, name, size ):

        self.__fonts[ f'{ name }:{ size }' ] = pygame.font.Font( self.get_path( filepath ), size )

    # Shortcut for blitting text to the screen (can choose origin :D)
    def draw_text( self, text, font, pos, color, anchor = ( 0, 0 ) ):

        text_surf = self.__fonts[ font ].render( text, True, color )
        pos.s( V2( anchor ).c().m( text_surf.get_size() ) )
        self.__screen.blit( text_surf, pos.l() )

    # Appends the input to the root directory
    def get_path( self, directory ):

        return self.__root_dir + directory

    # Initially loads the sprites into memory
    # Should only be called once
    def __load_sprites( self ):

        if ( len( self.__sprites ) != 0 ):
            raise ValueError( 'Sprites have already been initialized' )

        spr_file = open( self.get_path( '/textures/list.txt' ) ).read().split( '\n' )

        # Iterate through every line in the sprite file
        # sprites are listed as follows:
        # [name] = [relative filepath] [scale]:[# vertical subimages]:[# horizontal subimages]
        for line in spr_file:

            # Load the image and transform it based on the data in the file line
            line = line.split( ' = ' )
            surface = pygame.image.load( self.get_path( '/textures/' + line[1].split( ' ' )[0] ) )
            surface = pygame.transform.scale( surface, V2( surface.get_size() ).m( int( line[1].split( ' ' )[1].split( ':' )[0] ) ).l() )

            # Use the dimensions of the sprite divided by the # of subimages to get the size of a square
            dims = V2( surface.get_size() )
            square_count = V2( int( line[1].split( ' ' )[1].split( ':' )[1] ), int( line[1].split( ' ' )[1].split( ':' )[2] ) )
            square_size = dims.c().d( square_count )

            # Use the previous information to split the sprite up and append it to the sprite data
            self.__sprites[ line[0] ] = [ [ surface.subsurface( ( xx * square_size.x, yy * square_size.y, *square_size.l() ) ) for xx in range( square_count.x ) ]
                for yy in range( square_count.y ) ]

    # Returns one or multiple instances of a type
    def get_instance( self, instance_id ):

        if ( instance_id not in self.__named_instances or len( self.__named_instances[ instance_id ] ) == 0 ):
            return None
        return self.__named_instances[ instance_id ][0]

    def get_instances( self, instance_id ):

        if ( instance_id not in self.__named_instances or len( self.__named_instances[ instance_id ] ) == 0 ):
            return None
        return self.__named_instances[ instance_id ]

    # Returns a value from a dictionary if found,
    # otherwise returns the default value passed into the function
    @staticmethod
    def dict_search( dictionary, key, default ):
        
        return dictionary[ key ] if key in dictionary else default

    # Getters and setters
    @property
    def screen_size( self ):
        return self._screen_size

    @property
    def fps_limit( self ):
        return self._fps_limit

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
    def view_size( self ):
        return self._view_size