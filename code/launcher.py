from basic_imports import *
from _velocity_entity import *
from math import sin, e

class Launcher ( Velocity_Entity ):

    def __init__( self, engine, pos ):

        # This is the function used to compute the final velocity
        # It used to just multiply your current velocity by 2, but this allowed
        # for ridiculous amounts of speed
        # To solve this, I made the speed multiplier decrease as your velocity increased
        # You can view this graphically if you would like: https://www.desmos.com/calculator/uamj2t4hvp
        def vel_func( vel ):

            sign = utils.sign( vel )
            vel = abs( vel )
            sigmoid = 1 / ( 1 + e ** -( vel / 30 ) )
            sigmoid_transformed = 2 * ( 1 - sigmoid )
            return ( vel + sigmoid_transformed * vel ) * sign

        super().__init__( engine, 'launcher', pos, ( 1, 1, 0, 0 ), 'launcher', vel_func, ( 69, 122, 69 ), 'leaf' )