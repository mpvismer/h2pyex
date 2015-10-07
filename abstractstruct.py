'''
@author Mark Vismer
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

if __name__ == "__main__" and __package__ is None:
    from support import *
else:
    from .support import *


ENDIANNESS_LITTLE = '<'
ENDIANNESS_BIG = '>'
ENDIANNESS_NETWORK = '!'
ENDIANNESS_NATIVE = '='



class AbstractStruct(object):
    '''
    Abstract class for implementing struct classes.
    '''

    _frozen = False

    _packed_size = None

    def __init__(self):
        '''Constructor'''
        super(AbstractStruct, self).__init__()


    def __setattr__(self, key, value):
        '''
        Overrides base class.
        '''
        if self._frozen:
            if not hasattr(self, key):
                raise AttributeError('Struct class is "frozen". Cannot add attribute {}.'.format(key))
            if key.startswith('_'):
                raise AttributeError('Attribute {} is private and cannot be changed in a "frozen" class.'.format(key))
        super(AbstractStruct,self).__setattr__(key, value)

    def __delattr__(self, key):
        ''' Overrides base class. '''
        if self._frozen:
            raise AttributeError( "Parameter {} cannot be deleted.".format(key) )
        super(AbstractStruct,self).__delattr__(key)

    def __eq__(self, other):
        ''' Checks if two class have the same data. '''
        equal = False
        if isinstance(other, self.__class__):
            equal = self.serialise()==other.serialise()
            #for (key, val) in clsfields(self):
            #    if val != getattr(other, key, None):
            #        return False
            #equal = True
        return equal


    def __ne__(self, other):
        return not self.__eq__(other)

    def _indent_lines(self, complex_str):
        ''' Indents the lines in the string. '''
        lines = complex_str.splitlines()
        res = "  " + "\n  ".join(lines) + "\n"
        return res

    def freeze(self):
        ''' Freezes the struct class.'''
        self._frozen = True

    def packed_size(self):
        ''' Returns the packet size when serialized. '''
        return self._packed_size

    def deserialise(self, data):
        ''' Calls the deserialise_from buffer '''
        #assert len(data) >= self.packed_size() checked in deserialise_from() anyway
        self.deserialise_from(data, 0)

    def deserialise_from(self, buf, offset):
        ''' Deserilise a byte stream from a buffer.'''
        raise NotImplementedError(sys._getframe().f_code.co_name + " must be overridden.")

    def serialise(self):
        ''' Serialise a class to a byte stream.'''
        raise NotImplementedError(sys._getframe().f_code.co_name + " must be overridden.")

    def __repr__(self):
        '''
        Must be unambiguous.
        '''
        rep = "%s(  # @0x%08x\n" % (self.__class__.__name__, id(self))
        if hasattr(self, '_endianness'): rep += "  endianness = %r,\n" % self._endianness
        for field, val in clsfields(self):
            rep+= self._indent_lines("%s = %r," % (field, _adaptit(val)))
        rep += ')\n'
        return rep

    def __str__(self):
        ''' Multi-line pretty printing of the class's members. '''
        disp_str = self.__class__.__name__ + ":\n"
        for field, val in clsfields(self):
            disp_str+= self._indent_lines("%s = %s" % (field, _adaptit(val, True)))
        return disp_str

def _adaptit(val, abreviate=False):
    if hasattr(val, '__getitem__'):
        if abreviate and (len(val) > 8):
            return '[' + ', '.join([str(x) for x in val[:5]]) + ', ... ' + str(val[-1])+']'
        else:
            return val[:]
    else:
        return val


if __name__ == "__main__":
    AbstractStruct()

