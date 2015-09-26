'''
@author Mark Vismer
'''

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
    '''
    Abstract class for implementing struct classes based on the ctypes Structure.
    '''

    def __init__(self, **kwargs):
        super(CTypesStruct, self).__init__()
        fields =  getattr(self, '_fields_',[])
        for name, type_ in fields:
            if name in kwargs:
                val = getattr(self, name)
                initval = kwargs.pop(name)
                if hasattr(val,'__getitem__'):
                    #its an array
                    assert len(val) == len(initval)
                    getattr(self, name)[:] = initval
                else:
                    setattr(self, name, initval)

    def packed_size(self):
        ''' Returns the packet size when serialized. '''
        return ctypes.sizeof(self)

    def deserialise(self, buf):
        ''' Calls the deserialise_from buffer '''








        #     ctypes.addressof(self),
        #     utils.buffer_address(buf),
        #     size)

        utils.buffercpy(self, buf)

    def deserialise_from(self, buf, offset):
        ''' Deserialise a byte stream from a buffer.'''













        #    ctypes.addressof(self),
        #    info[0]+offset,
        #    size)






        #    ctypes.addressof(self),
        #    utils.buffer_address(buf) + offset,
        #    #buf[offset:size+offset],
        #    size)

        utils.buffercpy(self, buf, src_offset=offset)


    def serialise(self):
        ''' Serialise a class to a byte stream.'''
        return ctypes.string_at(ctypes.addressof(self), self.packed_size())



