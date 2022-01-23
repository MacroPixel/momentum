class StaticClass:

  _test_variable = 2

  @classmethod
  @property
  def test_variable( cls ):
    return cls._test_variable

  @classmethod
  def set_test_variable( cls, value ):
    cls._test_variable = value

print( StaticClass.test_variable )
rofl = StaticClass()
rofl.set_test_variable( 'ROFLcopter' )
print( rofl.test_variable )