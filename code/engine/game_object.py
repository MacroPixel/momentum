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
        self._tags = []
        self._properties = []
        self.__exists = True

        # Add the GameObject to the Engine
        self.engine.add_instance( self )

    # Remove from lists
    def delete( self ):

        if self.__exists:
            self.engine.delete_instance( self )
        self.__exists = False

    # Tags store information about an object
    # Objects within a specific tag can be easily searched for
    def add_tag( self, tag ):

        if ( tag not in self._tags ):
            self.engine.tag_instance( self, tag )
            self._tags.append( tag )

    def remove_tag( self, tag ):

        self.engine.untag_instance( self, tag )
        if tag in self._tags:
            self._tags.remove( tag )

    def has_tag( self, tag ):

        return ( tag in self.tags )

    # Properties are similar to tags, but are more performant
    # As a tradeoff, they don't allow search functionality
    def add_property( self, prop ):

        self._properties.append( prop )

    def remove_property( self, prop ):

        self._properties.remove( prop )

    def has_property( self, prop ):

        return ( prop in self._properties )

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

    @property
    def tags( self ):
        return self._tags.copy()

    @property
    def properties( self ):
        return self._properties.copy()