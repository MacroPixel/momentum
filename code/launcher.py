from basic_imports import *
from _velocity_entity import *
from math import sin

class Launcher ( Velocity_Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'launcher', pos.c().a( 0, -0.5 ), ( 0.8, 0.8, 0.4, 0.4 ), 'launcher', 2 )