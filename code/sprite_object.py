from game_object import *

# A more specialized GameObject designed for displaying a sprite
class SpriteObject ( GameObject ):

  # Create a sprite/position variable in addition to the normal setup
  def create_instance( self, sprite_surf, coords ):

    super().create_instance()
    self.sprite = sprite_surf
    self.pos = V2( coords )

  # Automatically draw the sprite
  def draw( self, engine ):

    engine.screen.blit( self.sprite, self.pos.l() )