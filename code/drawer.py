from basic_imports import *

# Tasked with running a draw function at a specific layer
class Drawer ( Game_Object ):

    def __init__( self, engine, layer, draw_function ):

        super().__init__( engine, 'drawer', layer = layer )

        # Store draw function for draw event
        self.__draw_function = draw_function

    # Run the designated draw function
    def draw( self ):

        self.__draw_function()