from .vector import *

# Stores a GameObject for later usage
def add_instance( self, game_object ):

    # "instances" holds every active GameObject
    self._Engine__instances.append( game_object )

    # "named_instances" allows searching for an object by name
    if game_object.object_id not in self._Engine__named_instances:
        self._Engine__named_instances[ game_object.object_id ] = []
    self._Engine__named_instances[ game_object.object_id ].append( game_object )

    # Insert into proper draw-order-position based on layer
    i = 0
    for i in range( len( self._Engine__draw_instances ) ):
        if self._Engine__draw_instances[i].layer > game_object.layer:
            break
    else:
        i += 1
    self._Engine__draw_instances.insert( i, game_object )

# Removes a GameObject from memory
def delete_instance( self, game_object ):

    if game_object in self._Engine__instances:
        self._Engine__instances.remove( game_object )
    if game_object in self._Engine__draw_instances:
        self._Engine__draw_instances.remove( game_object )
    if game_object in self._Engine__named_instances[ game_object.object_id ]:
        self._Engine__named_instances[ game_object.object_id ].remove( game_object )

    for tag in game_object.tags:
        if game_object in self._Engine__tagged_instances[ tag ]:
            self._Engine__tagged_instances[ tag ].remove( game_object )

# Adds a tag, which marks an object's properties, to an game object
# Safe to call on objects that already have the tag
def tag_instance( self, game_object, tag ):

    # "tagged_instances" stores a tag and all the game objects that have it
    # This implementation is very similar to __named_instances
    if tag not in self._Engine__tagged_instances:
        self._Engine__tagged_instances[ tag ] = []
    if game_object not in self._Engine__tagged_instances[ tag ]:
        self._Engine__tagged_instances[ tag ].append( game_object )

# Removes a tag from an instance
# Safe to call on objects that don't have the tag
def untag_instance( self, game_object, tag ):

    # "tagged_instances" stores a tag and all the game objects that have it
    # This implementation is very similar to __named_instances
    if tag in self._Engine__tagged_instances and game_object in self._Engine__tagged_instances[ tag ]:
        self._Engine__tagged_instances[ tag ].remove( game_object )

# Returns one or multiple instances of a type
def get_instance( self, instance_id ):

    if ( instance_id not in self._Engine__named_instances or len( self._Engine__named_instances[ instance_id ] ) == 0 ):
        return None
    return self._Engine__named_instances[ instance_id ][0]

def get_instances( self, instance_id ):

    if ( instance_id not in self._Engine__named_instances or len( self._Engine__named_instances[ instance_id ] ) == 0 ):
        return []
    return self._Engine__named_instances[ instance_id ]

# Returns one or multiple instances with a tag
def get_tagged_instance( self, tag ):

    if ( tag not in self._Engine__tagged_instances or len( self._Engine__tagged_instances[ tag ] ) == 0 ):
        return None
    return self._Engine__tagged_instances[ tag ][0]

def get_tagged_instances( self, tag ):

    if ( tag not in self._Engine__tagged_instances or len( self._Engine__tagged_instances[ tag ] ) == 0 ):
        return []
    return self._Engine__tagged_instances[ tag ]