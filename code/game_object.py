# An Object that receives update() and draw() events
class Game_Object:

    # Allows an object to be functional within the game
    def __init__( self, engine, object_id, layer = 0 ):

        # Make sure ID is value
        if ( str( object_id ) == '' ):
            raise ValueError( 'Object must have an ID' )

        # Store necessary variables
        self._layer = layer
        self._object_id = object_id
        self._engine = engine

        # Add the GameObject to the Engine
        self.engine.add_instance( self )

    # Remove from lists
    def delete( self ):

        self.engine.delete_instance( self )

    # Called once a frame
    def update( self ):
        pass

    # Called 10 times a second (for performance reasons)
    def tick( self ):
        pass

    # Draws stuff to the screen
    def draw( self ):
        pass

    # Getters/setters
    @property
    def layer( self ):
        return self._layer

    @property
    def object_id( self ):
        return self._object_id

    @property
    def engine( self ):
        return self._engine