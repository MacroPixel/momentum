import pygame
import random

# Initially loads the sounds into memory
# Should only be called once
def _load_sounds( self ):

    if ( len( self._Engine__sounds ) != 0 ):
        raise ValueError( 'Sounds have already been initialized' )

    sound_file = open( self.get_path( '/sounds/list.txt' ) ).read().split( '\n' )

    # Iterate through every line in the sound file
    # Sounds are listed as follows:
    # [name] = [SOUND/MUSIC] [relative filepath] [relative filepath] [relative filepath] [relative filepath] ...
    # Allows multiple filepaths to be specified
    for line in sound_file:

        # Parse through the data within the line of text
        internal_name, line = line.split( ' = ' )
        is_music_str = line.split( ' ' )[0]
        filenames = line.split( ' ' )[1:]

        # Determine if it's a sound or a song
        if ( is_music_str in [ 'SOUND', 'MUSIC' ] ):
            is_music = ( is_music_str == 'MUSIC' )
        else:
            raise ValueError( 'Invalid argument, should be SOUND or MUSIC' )

        # Load variants and store it if it's flagged as SOUND
        if not is_music:

            # Load all the sound's variants
            sounds = []
            for filename in filenames:
                sounds.append( pygame.mixer.Sound( self.get_path( '/sounds/' + filename ) ) )
            self._Engine__sounds[ internal_name ] = sounds

        # Otherwise, save the filename to music
        else:

            self._Engine__music[ internal_name ] = filenames[0]            

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

def play_music( self, name, volume = 1 ):

    # Play it
    pygame.mixer.music.load( self.get_path( '/sounds/' + self._Engine__music[ name ] ) )
    pygame.mixer.music.play( -1 )
    pygame.mixer.music.set_volume( volume )