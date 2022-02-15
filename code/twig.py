from basic_imports import *
from _velocity_entity import *
from math import sin

class Twig ( Velocity_Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'twig', pos.c().a( 0, -0.5 ), ( 0.8, 0.8, 0.4, 0.4 ), 'twig', 0.5 )