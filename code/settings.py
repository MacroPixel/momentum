from basic_imports import *

# Holds settings data, and allows drawing/changing of settings menu
class SettingsController:

    # Holds the number of settings
    SETTING_TOTAL = 3

    # Loads the settings dictionary
    def __init__( self, engine ):

        self.engine = engine
        self._settings = {}
        self._settings_pos = V2()

        data = open( self.engine.get_path( '/data/settings.txt' ) ).read()

        for line in data.split( '\n' ):

            # Ignore if blank line
            if ( len( line ) == 0 ):
                continue

            # Otherwise, store in dictionary
            setting_name, setting_value = line.split( ' = ' )
            self._settings[ setting_name ] = setting_value

        self.apply_settings()

    # Allows navigation of the settings menu
    # The setting_pos variable holds the 2d position of the selection
    # within the menu
    # This isn't clamped, and instead is %'ed every time it needs
    # to determine which option is currently selected
    def navigate_settings( self ):

        # Move cursor up and down (resets L/R position)
        if ( self.engine.get_key( pygame.K_UP, 1 ) ):
            self._settings_pos.y -= 1
            self._settings_pos.x = 0
        if ( self.engine.get_key( pygame.K_DOWN, 1 ) ):
            self._settings_pos.y += 1
            self._settings_pos.x = 0

        # Do specific actions for each one
        left_key = self.engine.get_key( pygame.K_LEFT, 1 )
        right_key = self.engine.get_key( pygame.K_RIGHT, 1 )

        # Sound and music volume
        if ( ( left_key or right_key ) and self._settings_pos.y in [ 0, 1 ] ):

            sound_music = 'sound_volume' if self._settings_pos.y == 0 else 'music_volume'
            addend = '-0.05' if self.engine.get_key( pygame.K_LEFT, 1 ) else '0.05'
            exec( f"self._settings[ '{ sound_music }' ] = str( utils.clamp( float( self._settings[ '{ sound_music }' ] ) + { addend }, 0, 1 ) )" )

            # Update data
            self.write()
            self.apply_settings( specific = ( 0 if sound_music == 'sound_volume' else 1 ) )

        # Timer
        if ( ( left_key or right_key ) and self._settings_pos.y == 2 ):

            self._settings[ 'show_timer' ] = ( '1' if self._settings[ 'show_timer' ] == '0' else '0' )

            # Update data
            self.write()

    # Draws the settings menu
    # There's a lot of boilerplate here but I don't really care enough to fix it
    def draw_settings( self ):

        self.engine.draw_text_bitmap( 'Settings', 'main', 4, V2( self.engine.screen_size.x / 2, 50 ), True, anchor = V2( 0.5, 0 ) )

        current_pos = V2( self.engine.screen_size.x / 2, 150 )
        current_str = f"Sound volume: { round( float( self._settings[ 'sound_volume' ] ) * 100 ) }%"
        self.engine.draw_text_bitmap( current_str, 'main', 2, current_pos, True, anchor = V2( 0.5, 0 ), color = self._check_color( 0 ) )
        current_pos.a( 0, 40 )
        current_str = f"Music volume: { round( float( self._settings[ 'music_volume' ] ) * 100 ) }%"
        self.engine.draw_text_bitmap( current_str, 'main', 2, current_pos, True, anchor = V2( 0.5, 0 ), color = self._check_color( 1 ) )
        current_pos.a( 0, 40 )
        current_str = f"Timer: { 'Shown' if self._settings[ 'show_timer' ] != '0' else 'Hidden' }"
        self.engine.draw_text_bitmap( current_str, 'main', 2, current_pos, True, anchor = V2( 0.5, 0 ), color = self._check_color( 2 ) )

    # Takes a y-index of a setting in the grid, and
    # returns the color that should be used
    # Returns white if deselected and green if selected
    def _check_color( self, index ):

        return ( 0, 255, 0 ) if ( self._settings_pos.y % self.SETTING_TOTAL == index ) else ( 255, 255, 255 )

    # Write the setting dictionary to the file
    def write( self ):

        try:

            file = open( self.engine.get_path( '/data/settings.txt' ), 'w' )

            for setting_name, setting_value in self._settings.items():
                file.write( f'{ setting_name } = { setting_value }\n' )

        finally:
            file.close()

    def get_setting( self, name ):

        return self._settings[ name ]

    # Applies any side effects changing the settings should have
    # Can be set to only change a specific settings
    def apply_settings( self, specific = None ):

        # Use the SQUARE ROOT of the volume to make it more in line with
        # how human ears perceive sound
        if ( specific is None or specific == 0 ):
            self.engine.set_sound_volume( float( self._settings[ 'sound_volume' ] ) ** 2 )
        if ( specific is None or specific == 1 ):
            self.engine.set_music_volume( float( self._settings[ 'music_volume' ] ) ** 2 )