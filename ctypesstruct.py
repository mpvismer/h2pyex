"""
@author Mark Vismer
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import ctypes


from .support import *
from .abstractstruct import *



class CTypesStruct(AbstractStruct):
    """
    Abstract class for implementing struct classes based on the ctypes Structure.
    """
    
    def __init__(self, **kwargs):
        super(CTypesStruct, self).__init__()
        self.freeze()
        
        for key, val in enum_fields(kwargs):
            setattr(self, key, val)
        
        #fields =  getattr(self, '_fields_',[])
        #for name, type_ in fields:
        #    if name in kwargs:
        #        #val = getattr(self, name)
        #        initval = kwargs.pop(name)
        #        setattr(self, name, initval)
    
    def packed_size(self):
        """ Returns the packet size when serialized. """
        return ctypes.sizeof(self)
    
    def deserialise(self, buf):
        """ Calls the deserialise_from buffer """
        #     ctypes.addressof(self),
        #     utils.buffer_address(buf),
        #     size)
        return utils.buffer_move(self, buf)
    
    def deserialise_from(self, buf, offset):
        """ Deserialise a byte stream from a buffer."""
        #    ctypes.addressof(self),
        #    info[0]+offset,
        #    size)
        #    ctypes.addressof(self),
        #    utils.buffer_address(buf) + offset,
        #    #buf[offset:size+offset],
        #    size)
        return utils.buffer_move(self, buf, src_offset=offset)
    
    
    def serialise(self):
        """
        Serialise a class to a raw data.
        """
        return str(self.const_data())
    
    
    def serialise_into(self, buf, offset=0):
        """
        Serialise a class into a mutable buffer.
        """
        #copied = self.packed_size()
        #buf[offset:self.packed_size()] = self.const_data()[:] # Indexing helps with data type compatibility - python should optimise this anyway so should not make a speed difference.
        return utils.buffer_move(buf, self, dst_offset=offset)
    
    
    def data(self):
        """
        Return the data in this struct as a packed mutable byte array whose data shares the
        memory buffer of the struct.
        """
        raise memoryview(self)
    
    
    def const_data(self):
        """
        Return the data in this struct as a packed string which shares the memory buffer
        of the struct.
        """
        return ctypes.string_at(ctypes.addressof(self), self.packed_size())




