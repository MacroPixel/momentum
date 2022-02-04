import pygame
import random

def play_sound( self, name, variant = -1 ):

    # Get the list of sound variants
    if name not in self._Engine__sounds:
        raise KeyError( f'Unknown sound "{ name }"' )
    sound_list = self._Engine__sounds[ name ]

    # Get variant (make sure it's within bounds)
    # -1 chooses a random variant
    if ( variant == -1 ):
        variant = random.randint( 0, len( sound_list ) - 1 )
    elif not ( 0 <= variant < len( sound_list ) ):
        raise IndexError( f'Invalid variant, allowed range for "{ name }" is [0, { len( sound_list ) - 1 }]' )

    # Play the sound
    sound_list[ variant ].play()