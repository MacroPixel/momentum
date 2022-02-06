from basic_imports import *

# Recreates the level data from a PNG image
def rewrite_level( self ):

    # Load the PNGs into memory
    block_surf = pygame.image.load( controller.engine.get_path( '/data/level.png' ) )

    keys = {} # The position of every block in the PNG
    origin = V2( 0, 0 ) # Where the player spawns

    # Loop through all the pixels in the PNG
    for xx in range( block_surf.get_width() ):
        for yy in range( block_surf.get_height() ):

            pos = V2( xx, yy )

            # Create the player if the pixel is white
            if block_surf.get_at( pos.l() ) == ( 255, 255, 255, 255 ):
                origin = pos

            # Otherwise, create the appropriate block based on color
            else:
                for i in range( 1, B_TOTAL ):
                    if block_surf.get_at( pos.l() ) == B_COLORS[i]:
                        keys[ utils.vec_to_str( pos ) ] = i

    # Store the real position of every block,
    # relative to the origin instead of top-left of image
    chunks = {}

    for pos in keys:

        new_pos = utils.str_to_vec( pos ).s( origin )
        chunk_pos = new_pos.c().d( C_GRID ).fn( lambda a: int( floor( a ) ) )
        chunk_str = utils.vec_to_str( chunk_pos )

        if chunk_str not in chunks:
            chunks[ chunk_str ] = {}
        chunks[ chunk_str ][ utils.vec_to_str( new_pos.c().s( chunk_pos.c().m( C_GRID ) ) ) ] = keys[ pos ]

    # Actually write to the file
    file = open( controller.engine.get_path( '/data/blocks.txt' ), 'w' )
    for chunk in chunks:

        file.write( f'* { chunk }\n' )

        for block_pos in chunks[ chunk ]:

            file.write( f'{ B_STRINGS[ chunks[ chunk ][ block_pos ] ] } { block_pos.replace( ":", " " ) }\n' )