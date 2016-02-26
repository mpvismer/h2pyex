'''
@author Mark Vismer

'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals



class UndefinedException(SyntaxError):
    """
    This is a base class for a formatted exception which is associated with a
    particular line number.
    """
    def __init__(self, contents, lineno=None):
        '''
        Constructor
        '''
        self.msg = contents
        self.lineno = lineno

    def __str__(self):
        if self.lineno is None:
            return self.msg
        else:
            return 'Line {}, was "{}"'.format(self.lineno, self.msg)


class ParseException(UndefinedException):
    """
    For parsing errors - generally a c syntax error or something that just
    can't be handled.
    """
    pass

class UnexpectedException(ParseException):
    """
    A more specifc version of a ParseException for some sort of unexepected contenets.
    """
    pass

class UnsupportedDataTypeException(UndefinedException):
    """
    For when unsupported data types are discovered.
    """
    pass



