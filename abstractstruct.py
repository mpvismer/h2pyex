"""
@author Mark Vismer
"""

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
    """
    Abstract class for implementing struct classes.
    """
    
    _frozen = False
    
    _packed_size = None
    
    def __init__(self):
        """Constructor"""
        super(AbstractStruct, self).__init__()
    
    
    def __setattr__(self, name, value, allow_private=False):
        """
        Overrides base class.
        """
        def set_struct(obj, newval):
            if isinstance(newval, AbstractStruct):
                obj.deserialise(newval.serialise())
            else:
                for key, val in enum_fields(newval):
                    setattr(obj, key, val)
        
        def set_array(obj, newval):
            assert hasattr(obj, '__getitem__')
            if len(newval) > len(obj):
                raise ValueError("Attribute '{}' has invalid length.".format(str(newval)))
            newval_len = len(newval)
            if 0 == newval_len:
                return
            elif isinstance(obj[0], AbstractStruct):
                for idx in range(0, newval_len):
                    assert isinstance(obj[idx], AbstractStruct)
                    set_struct(obj[idx], newval[idx]);
            elif isstr(obj[0]):
                for i in range(newval_len):
                    _newval = newval[i]
                    if not isstr(_newval):
                        raise ValueError("Incorrect value {} of type {}. Expected a str.".format(_newval, type(_newval)))
                    obj[i] = str(_newval)
            elif hasattr(obj[0], '__getitem__'):
                for idx in range(0, newval_len):
                    set_array(obj[idx], newval[idx])
            
            else:
                obj[:newval_len] = newval[:newval_len]
        
        if self._frozen:
            if not hasattr(self, name):
                raise AttributeError('Struct class is "frozen". Cannot add new attribute {}.'.format(name))
            if (not allow_private) and name.startswith('_'):
                raise AttributeError('Attribute {} is private and cannot be changed in a "frozen" class.'.format(name))
        
        oldval = getattr(self, name, None)
        if isinstance(oldval, AbstractStruct):
            set_struct(oldval, value)
        elif hasattr(oldval,'__getitem__') and not isstr(oldval):
            set_array(oldval, value)
        else:
            super(AbstractStruct,self).__setattr__(name, value)
    
    def __delattr__(self, key):
        """
        Overrides base class.
        """
        if self._frozen:
            raise AttributeError( "Parameter {} cannot be deleted.".format(key) )
        super(AbstractStruct,self).__delattr__(key)
    
    
    def __eq__(self, other):
        """
        Checks if two class have the same data.
        """
        if isinstance(other, AbstractStruct):
            return self.serialise()==other.serialise()
        else:
            return Exception("TODO")
    
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    
    def freeze(self):
        """
        Freezes the struct class.
        """
        self._frozen = True
    
    
    def packed_size(self):
        """
        Returns the packet size when serialized.
        """
        return self._packed_size
    
    
    def deserialise(self, data):
        """
        Calls the deserialise_from buffer
        """
        #assert len(data) >= self.packed_size() checked in deserialise_from() anyway
        self.deserialise_from(data, 0)
    
    
    def deserialise_from(self, buf, offset):
        """
        Deserilise a byte stream from a buffer.
        """
        raise NotImplementedError(sys._getframe().f_code.co_name + " must be overridden.")
    
    
    def serialise(self):
        """
        Serialise a class to a raw data.
        """
        raise NotImplementedError(sys._getframe().f_code.co_name + " must be overridden.")
    
    
    def serialise_into(self, buf):
        """
        Serialise a class into a mutable buffer.
        """
        raise NotImplementedError(sys._getframe().f_code.co_name + " must be overridden.")
    
    def data(self):
        """
        Return the data in this struct as a packed mutable byte array whose data shares the
        memory buffer of the struct.
        """
        raise NotImplementedError(sys._getframe().f_code.co_name + " is not supported.")
    
    def const_data(self):
        """
        Return the data in this struct as a packed string which shares the memory buffer
        of the struct.
        """
        raise NotImplementedError(sys._getframe().f_code.co_name + " is not supported.")
    
    
    def update(self, other, accessor='', verbose=False):
        """
        Tries to update the fields of this structure with those from other.
        """
        updated = False
        for key, val in enum_fields(other):
            updated |= self.update_field(key, val, accessor, verbose)
        return updated
    
    
    def update_field(self, name, val, accessor='', verbose=False):
        """
        Updates the field in the structure named <name> only if is different.
        """
        def update_array(obj, newval, accessor, verbose):
            assert hasattr(obj, '__getitem__')
            updated = False
            mlen = min(len(obj), len(newval))
            if (mlen > 0):
                if isinstance(obj[0], AbstractStruct):
                    for idx in range(0, mlen):
                        assert isinstance(obj[idx], AbstractStruct)
                        updated |= obj[idx].update(newval[idx], accessor+'[{}]'.format(idx), verbose=verbose)
                elif hasattr(obj[0], '__getitem__') and not isstr(obj[0]):
                    for idx in range(0, mlen):
                        assert hasattr(obj[idx], '__getitem__')
                        updated |= update_array(obj[idx], newval[idx], accessor+'[{}]'.format(idx), verbose=verbose)
                elif hasattr(obj, '__ctypes_from_outparam__') and isstr(obj[0]):
                    if isstr(newval):
                        newval = str(newval+'\0'*(len(obj)-mlen))
                        mlen = len(obj)
                    if obj[:]!=newval[:]:
                        updated = True
                        msg = 'Updating string {}, from {}'.format(accessor, repr(obj[:].strip('\0')))
                        obj[:] = newval[:]
                        msg += ' to {}.'.format(repr(obj[:]).strip('\0'))
                        show_it(msg)
                elif (obj[:mlen]!=newval[:mlen]):
                    updated = True
                    msg = 'Updating array in field {}, from {}'.format(accessor, repr(obj[:]))
                    obj[:mlen] = newval[:mlen]
                    msg += ' to {}.'.format(repr(obj[:]))
                    show_it(msg)
                if mlen < len(newval):
                    msg = 'WARNING: Indexes {}:{} ignored of {} because out of range.'.format(
                        mlen, len(newval), type(self).__name__)
                    show_it(msg)
            return updated
        
        def show_it(msg):
            _logger.debug(msg)
            if verbose:
                print(msg)
        
        updated = False
        oldval = getattr(self, name, None)
        if isinstance(oldval, AbstractStruct):
            updated |= oldval.update(val, accessor+'.'+name, verbose=verbose)
        elif hasattr(oldval, '__getitem__') and not isstr(oldval[:]):
            updated |= update_array(oldval, val, accessor+'.'+name, verbose=verbose)
        elif oldval is None:
            msg = 'WARNING: Field "{}={}" could not be updated because it does not exist in "{}".'.format(
                    name, repr(val), type(self).__name__)
            show_it(msg)
        else:
            if oldval!=val:
                updated = True
                msg = 'Updating field {}={} to {}.'.format(name,repr(oldval), repr(val))
                setattr(self, name, val)
                show_it(msg)
        return updated
    
    
    def pythonise(self):
        """
        Convert to python objects - structs to dictionaries and arrays to lists.
        """
        def convert_val(val):
            if isinstance(val, AbstractStruct):
                res = val.pythonise()
            elif hasattr(val, '__getitem__'):
                if isstr(val[:]):
                    res = str(val[:])
                else:
                    res = list(convert_val(item) for item in val)
            else:
                res = val
            return res
        d = {}
        for field, val in enum_fields(self):
            d[field] = convert_val(val)
        return d
    
    
    def __repr__(self):
        """
        Must be unambiguous.
        """
        rep = "%s(" % (self.__class__.__name__)
        if hasattr(self, '_endianness'): rep += "\n  endianness=%r," % self._endianness
        lines = []
        for field, val in enum_fields(self):
            lines.append(_indent_lines("%s=%s" % (field, _stringit(val, fn=repr))))
        rep += '\n' + ',\n'.join(lines)
        rep += ')'
        return rep
    
    
    def __str__(self):
        """ Multi-line pretty printing of the class's members. """
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
            if isstr(val):
                return repr(val)
            elif len(val)==0:
                return '[]'
            elif isinstance(val[0], AbstractStruct):
                return '[\n' + ',\n'.join([_indent_lines(fn(x)) for x in val]) + '\n]'
            elif hasattr(val[0], '__getitem__'):
                return '[\n' + ',\n'.join([_indent_lines(_stringit(x, fn=fn)) for x in val]) + '\n]'
            else:
                _logger.warning("This should never happen!")
                return fn(val[:])
    else:
        return fn(val)


def _indent_lines(complex_str):
    """ Indents the lines in the string. """
    lines = complex_str.splitlines()
    res = "  " + "\n  ".join(lines)
    return res


if __name__ == "__main__":
    AbstractStruct()

