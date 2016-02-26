'''
@author Mark Vismer
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import logging

if __name__ == "__main__" and __package__ is None:
    from support import *
else:
    from .support import *

_logger = logging.getLogger(__name__)


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


    def __setattr__(self, key, value, allow_private=False):
        '''
        Overrides base class.
        '''
        def set_array(obj, newobj):
            assert hasattr(obj, '__getitem__')
            if len(obj)==0:
                return
            if isinstance(obj[0], AbstractStruct):
                for idx in range(0, len(obj)):
                    assert isinstance(obj[idx], AbstractStruct)
                    for key, val in enum_fields(newobj[idx]):
                        setattr(obj[idx], key, val)
            elif isstr(obj):
                obj = newobj
            elif hasattr(obj[0], '__getitem__'):
                for idx in range(0, len(obj)):
                    set_array(obj[idx], newobj[idx])
            else:
                obj[:] = newobj[:]

        if self._frozen:
            if not hasattr(self, key):
                raise AttributeError('Struct class is "frozen". Cannot add attribute {}.'.format(key))
            if (not allow_private) and key.startswith('_'):
                raise AttributeError('Attribute {} is private and cannot be changed in a "frozen" class.'.format(key))

        oldval = getattr(self, key, None)
        if isstr(oldval):
            super(AbstractStruct,self).__setattr__(key, value)
        elif isinstance(oldval, AbstractStruct):
            if isinstance(value, AbstractStruct):
                getattr(self, key).deserialise(value.serialise())
            else:
                _logger.debug('Attempting to update struct field "%s" from %s.', (key, value))
                getattr(self, key).update(value)
        elif hasattr(oldval,'__getitem__'):
            set_array(oldval, value)
        else:
            super(AbstractStruct,self).__setattr__(key, value)


    def __delattr__(self, key):
        ''' Overrides base class. '''
        if self._frozen:
            raise AttributeError( "Parameter {} cannot be deleted.".format(key) )
        super(AbstractStruct,self).__delattr__(key)


    def __eq__(self, other):
        ''' Checks if two class have the same data. '''
        equal = False
        if isinstance(other, AbstractStruct):
            equal = self.serialise()==other.serialise()
            #for (key, val) in enum_fields(self):
            #    if val != getattr(other, key, None):
            #        return False
            #equal = True
        return equal


    def __ne__(self, other):
        return not self.__eq__(other)


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


    def update(self, other, verbose=False):
        '''
        Tries to update the fields of this structure with those from other.
        '''
        updated = False
        for key, val in enum_fields(other):
            updated |= self.update_field(key, val, verbose)
        return updated


    def update_field(self, name, val, verbose=False):
        '''
        Updates the field in the structure named <name> only if is different.
        '''
        def update_array(obj, val, verbose):
            updated = False
            if len(obj)==0:
                return
            mlen = min(len(obj), len(val))
            if (mlen > 0):
                if obj[:mlen]!=val[:mlen]:
                    if isinstance(obj[0], AbstractStruct):
                        for idx in range(0, mlen):
                            assert isinstance(obj[idx], AbstractStruct)
                            updated |= obj[idx].update(val[idx], verbose=verbose)
                    elif hasattr(obj[0], '__getitem__'):
                        for idx in range(0, mlen):
                            assert hasattr(obj[idx], '__getitem__')
                            updated |= update_array(obj[idx], val[idx], verbose=verbose)
                    else:
                        msg = 'Existing field array "{}={}" updating to "{}".'.format(name, obj[:], val[:])
                        updated = True
                        obj[:mlen] = val[:mlen]
                        show_it(msg)
            return updated

        def show_it(msg):
            _logger.debug(msg)
            if verbose:
                print(msg)

        updated = False
        field = getattr(self, name, None)
        if field is None:
            msg = 'WARNING: Field "{}={}" could not be updated because it does not exist in "%s".'.format(
                    name, str(val), type(self).__name__)
            show_it(msg)
        elif isinstance(field, AbstractStruct):
            updated |= field.update(val, verbose=verbose)
        elif hasattr(field, '__getitem__'):
            updated |= update_array(field, val, verbose=verbose)
        else:
            if field!=val:
                updated = True
                msg = 'Existing field "{}={}" updating to "{}".'.format(name, field, val)
                setattr(self, name, val)
                show_it(msg)
        return updated


    def pythonise(self):
        '''
        Convert to python objects - structs to dictionaries and arrays to lists.
        '''
        def convert_val(val):
            if isinstance(val, AbstractStruct):
                res = val.pythonise()
            elif hasattr(val, '__getitem__'):
                res = list(convert_val(item) for item in val)
            else:
                res = val
            return res
        d = {}
        for field, val in enum_fields(self):
            d[field] = convert_val(val)
        return d


    def __repr__(self):
        '''
        Must be unambiguous.
        '''
        rep = "%s(" % (self.__class__.__name__)
        if hasattr(self, '_endianness'): rep += "\n  endianness=%r," % self._endianness
        lines = []
        for field, val in enum_fields(self):
            lines.append(_indent_lines("%s=%s" % (field, _stringit(val, fn=repr))))
        rep += '\n' + ',\n'.join(lines)
        rep += ')'
        return rep


    def __str__(self):
        ''' Multi-line pretty printing of the class's members. '''
        disp_str = self.__class__.__name__ + "@0x%08x:" % id(self)
        wasField = False
        for field, val in enum_fields(self):
            disp_str+= "\n" + _indent_lines("%s = %s" % (field, _stringit(val, True)))
            wasField = True
        if not wasField:
            disp_str += "\n" + _indent_lines("<empty struct>")
        return disp_str


def _stringit(val, abreviate=False, fn=str):
    if hasattr(val, '__getitem__'):
        if abreviate and (len(val) > 8):
            if isinstance(val[0], AbstractStruct):
                return '[\n' + ',\n'.join([_indent_lines(fn(x)) for x in val[:6]]) + ',\n  ...\n  ' + fn(val[-1])+'\n]'
            elif hasattr(val[0], '__getitem__'):
                return '[\n' + ',\n'.join([_indent_lines(_stringit(x, fn=fn)) for x in val]) + '\n]'
            else:
                return '[' + ', '.join([fn(x) for x in val[:6]]) + ', ... ' + fn(val[-1])+']'
        else:
            if len(val)==0:
                if fn==str:
                    return '[null]'
                else:
                    return '[]'
            elif isinstance(val[0], AbstractStruct):
                return '[\n' + ',\n'.join([_indent_lines(fn(x)) for x in val]) + '\n]'
            elif hasattr(val[0], '__getitem__'):
                return '[\n' + ',\n'.join([_indent_lines(_stringit(x, fn=fn)) for x in val]) + '\n]'
            else:
                return fn(val[:])
    else:
        return fn(val)


def _indent_lines(complex_str):
    ''' Indents the lines in the string. '''
    lines = complex_str.splitlines()
    res = "  " + "\n  ".join(lines)
    return res


if __name__ == "__main__":
    AbstractStruct()

