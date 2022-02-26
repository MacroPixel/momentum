from basic_imports import *
from _velocity_entity import *
from math import sin

class Twig ( Velocity_Entity ):

    def __init__( self, engine, pos ):

        super().__init__( engine, 'twig', pos, ( 1, 1, 0, 0 ), 'twig', lambda a: a * 0.5, ( 107, 77, 49 ), 'stick' )