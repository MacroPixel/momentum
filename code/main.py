def main():

    # Read the filepath from the path file
    # Defaults to /res
    try:
        res_path = open( 'res_path.txt' ).read()
    except FileNotFoundError:
        res_path = '/momentum/res'

    g_engine = Engine( V2( 1280, 720 ), 'Momentum',
        room_dict = ROOM_DICT,
        start_room = 'splash',
        root_dir = os.path.dirname( os.getcwd() ) + res_path,
        icon_source = '/textures/icon.png',
        fps_limit = 0,
        zoom_level = V2( 3, 3 )
    )
    g_engine.run()

if __name__ == '__main__':

    try:

        from engine.engine import *

        import pygame
        import os
        import traceback

        from constants import *
        from rooms import *

        main()

    except:
        
        open( 'error.txt', 'w' ).write( traceback.format_exc() )