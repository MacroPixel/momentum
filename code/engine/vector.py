# Compact vector class
class V2:

  def __init__( self, a = 0, b = 0 ):

    if isinstance( a, V2 ):
      self.u( a.x, a.y )
    elif type( a ) == list or type( a ) == tuple:
      self.u( a[0], a[1] )
    else:
      self.u( a, b )

  # These two functions help to reduce repetitive code within the operation functions
  def _op( self, a, b, op ):

    if op == '+': return a + b
    elif op == '-': return a - b
    elif op == '*': return a * b
    elif op == '/': return a / b
    elif op == 'fn': return b( a )

  def _op2( self, a, b, op ):

    if isinstance( a, V2 ):
      self.x = self._op( self.x, a.x, op )
      self.y = self._op( self.y, a.y, op )
    elif type( a ) == list or type( a ) == tuple:
      self.x = self._op( self.x, a[0], op )
      self.y = self._op( self.y, a[1], op )
    else:
      self.x = self._op( self.x, a, op )
      self.y = self._op( self.y, a if b == 'd' else b, op )

  # Update
  def u( self, a = 0, b = 0 ):

    self.x = a
    self.y = b
    return self

  # Add
  def a( self, a, b = 'd' ):
    self._op2( a, b, '+' )
    return self

  # Subtract
  def s( self, a, b = 'd' ):
    self._op2( a, b, '-' )
    return self

  # Multiply
  def m( self, a, b = 'd' ):
    self._op2( a, b, '*' )
    return self

  # Divide
  def d( self, a, b = 'd' ):
    self._op2( a, b, '/' )
    return self

  # Custom function
  def fn( self, a, b = 'd' ):
    self._op2( a, b, 'fn' )
    return self
    
  # Return a list
  def l( self ):
    return [ self.x, self.y ]

  # Cast to int
  def i( self ):

    self.x = int( self.x )
    self.y = int( self.y )
    return self

  # Return a copy
  def c( self ):
    c = V2( self.x, self.y )
    return c

  # Return a string
  def __str__( self ):
    return f'({ self.x }, { self.y })'

  # Allows using as key in dictionary
  # Simply hashes a tuple representation of the vector
  def __hash__( self ):
    return hash( ( self.x, self.y ) )

  # Compares two vectors
  def __eq__( self, other ):
    if isinstance( other, V2 ):
      return self.x == other.x and self.y == other.y
    return False