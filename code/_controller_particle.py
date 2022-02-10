from basic_imports import *
from drawer import *
from math import sin, cos, pi
import random

class ParticleController:

    def __init__( self, controller ):

        # Parent objects
        self._controller = controller
        self.__engine = self.controller.engine

        # A "simple particle" moves with a constant velocity
        # all_simple holds a dictionary representation of every simple particle
        self.__all_simple = []

        # Delegate draw function to drawer, which can draw at the proper layer
        Drawer( self.__engine, LAYER_PARTICLE, self.draw )

    def update( self ):

        # Particles don't move if the game is paused
        if ( self.controller.pause_level != PAUSE_NONE ):
            return

        # Update all simple particles
        for particle in self.__all_simple:
            self.update_simple( particle )

    def draw( self ):

        # Draw all simple particles
        for particle in self.__all_simple:
            self.draw_simple( particle )

    # Creates a specific particle types
    def create_simple( self, pos, speed_range, angle_range, size_range, color_list, fade_time_range, fade_start_range = ( 1, 1 ) ):

        speed = random.uniform( *speed_range[:2] )
        angle = random.uniform( *angle_range[:2] ) * ( pi / 180 )
        size = random.randint( *size_range[:2] )
        color = random.choice( color_list )
        fade_time = random.uniform( *fade_time_range[:2] )
        fade_start = random.uniform( *fade_start_range[:2] )

        vel = V2( cos( angle ), sin( angle ) ).m( speed )

        self.__all_simple.append( {
            'pos': pos.c(),
            'vel': vel,
            'size': size,
            'color': color,
            'fade_time': fade_time,
            'fade_value': fade_start
        } )

    # Update a specific particle type
    def update_simple( self, particle ):

        particle[ 'pos' ].a( particle[ 'vel' ].c().m( self.__engine.delta_time ) )
        particle[ 'fade_value' ] -= ( 1 / particle[ 'fade_time' ] ) * self.__engine.delta_time

        if ( particle[ 'fade_value' ] <= 0 ):
            self.__all_simple.remove( particle )

    # Draw a specific particle type
    def draw_simple( self, particle ):

        surf = pygame.Surface( ( particle[ 'size' ], particle[ 'size' ] ), pygame.SRCALPHA, 32 )
        surf.fill( ( *particle[ 'color' ], min( 1, particle[ 'fade_value' ] ) * 255 ) )
        self.__engine.draw_surface( surf, particle[ 'pos' ].c().m( GRID ), False )

    # Getters/setters

    @property
    def controller( self ):
        return self._controller