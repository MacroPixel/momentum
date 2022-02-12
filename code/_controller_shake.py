from basic_imports import *
import random
from math import sin, cos, pi

# Gets rid of any screen shake on the controller
# Should also be called in init
def shake_reset( self ):

    self._view_shake = V2()
    self._screen_shake = None

# Adds a screen shake to the controller for a set amount of time
def shake_screen( self, amount, time, interval = 0.15 ):

    self._screen_shake = {
        'amount': amount,
        'time_left': time,
        'time': time
    }

def update_shake( self ):

    # Ignore if None is set
    if self._screen_shake is None:
        return

    # Just set to random values for now
    am = self._screen_shake[ 'amount' ] * ( self._screen_shake[ 'time_left' ] / self._screen_shake[ 'time' ] ) ** 2
    self._view_shake = V2( random.uniform( -am, am ), random.uniform( -am, am ) )

    # Set to none if timer is done
    self._screen_shake[ 'time_left' ] -= self.engine.delta_time
    if ( self._screen_shake[ 'time_left' ] <= 0 ):
        self.shake_reset()