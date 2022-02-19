from engine.engine import *
from constants import *
from utils import *

# Responsible for loading strings from external files
class lang:

    @classmethod
    def load( cls, engine ):

        cls.ABILITY_INFO = open( engine.get_path( '/data/lang/ability_info.txt' ) ).read().split( '\n<NEXT>\n' )
        cls.ABILITY_INFO = [ line.split( '\n' ) for line in cls.ABILITY_INFO ]

        cls.DEATH_STRINGS = open( engine.get_path( '/data/lang/death_strings.txt' ) ).read().split( '\n' )