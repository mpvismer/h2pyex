"""
@author Mark Vismer
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ctypes import *

from .writer import *


TYPE_2_CTYPE_MAP = {
    'bool'      : c_bool,
    'bool_t'    : c_bool,
    
    'char'      : c_char,
    'char_t'      : c_char,
    
    'int8_t'    : c_byte,
    'uint8_t'   : c_ubyte,
    'int16_t'   : c_short,
    'uint16_t'  : c_ushort,
    'int32_t'   : c_int,
    'uint32_t'  : c_uint,
    'int64_t'   : c_longlong,
    'uint64_t'  : c_ulonglong,
    
    'INT8'      : c_byte,
    'UINT8'     : c_ubyte,
    'INT16'     : c_short,
    'UINT16'    :  c_ushort,
    'INT32'     : c_int,
    'UINT32'    : c_uint,
    'INT64'     : c_longlong,
    'UINT64'    : c_ulonglong,
    
    'float'     : c_float,
    'double'    :  c_double,
    
    'float32_t' : c_float,
    'float64_t' : c_double
}

TYPE_2_CTYPESTR_MAP = {
    'bool'      : 'ctypes.c_bool',
    'bool_t'    : 'ctypes.c_bool',
    
    'char'      : 'ctypes.c_char',
    'char_t'      : 'ctypes.c_char',
    
    'int8_t'    : 'ctypes.c_byte',
    'uint8_t'   : 'ctypes.c_ubyte',
    'int16_t'   : 'ctypes.c_short',
    'uint16_t'  : 'ctypes.c_ushort',
    'int32_t'   : 'ctypes.c_int',
    'uint32_t'  : 'ctypes.c_uint',
    'int64_t'   : 'ctypes.c_longlong',
    'uint64_t'  : 'ctypes.c_ulonglong',
    
    'INT8'      : 'ctypes.c_byte',
    'UINT8'     : 'ctypes.c_ubyte',
    'INT16'     : 'ctypes.c_short',
    'UINT16'    : 'ctypes.c_ushort',
    'INT32'     : 'ctypes.c_int',
    'UINT32'    : 'ctypes.c_uint',
    'INT64'     : 'ctypes.c_longlong',
    'UINT64'    : 'ctypes.c_ulonglong',
    
    'float'     : 'ctypes.c_float',
    'double'    : 'ctypes.c_double',
    
    'float32_t' : 'ctypes.c_float',
    'float64_t' : 'ctypes.c_double'
}


ENDIANNESS_MAP = {
    ENDIANNESS_NETWORK : 'ctypes.BigEndianStructure',
    ENDIANNESS_BIG:'ctypes.BigEndianStructure',
    ENDIANNESS_LITTLE:'ctypes.LittleEndianStructure',
    ENDIANNESS_NATIVE:'ctypes.Structure'
    }

class WriterCTypes(Writer):
    """
    A modified verson of Writer to create a class where ctypes are used.
    """
    def __init__(self, **kwargs):
        super(WriterCTypes, self).__init__(type_map=TYPE_2_CTYPESTR_MAP, **kwargs)
    
    def _check_dependencies(self):
        if not self.has_dependencies:
            #self.putln("# For python 3 compatibility")
            #self.putln("from __future__ import absolute_import")
            #self.putln("from __future__ import division")
            #self.putln("from __future__ import print_function")
            #self.putln("from __future__ import unicode_literals")
            #self.putln()
            self.putln("import ctypes")
            self.putln("from h2pyex.ctypesstruct import CTypesStruct")
            self.has_dependencies = True
    
    def write_struct_class(self, structname, structcomment, members, final_comment=''):
        self._check_dependencies()
        self.putln("class {}(CTypesStruct, {}):".format(structname, ENDIANNESS_MAP[self.default_endianness]))
        self.put_doc_comment(structcomment + "\n" + final_comment,1)
        self.putln1("_fields_ = [")
        for (attribname, typename, dimensions, comment) in members:
            if dimensions:
                typestring = self.type_map[typename]
                for dim in reversed(dimensions):
                    typestring = '({}*{})'.format(typestring, dim)
                self.putln2("('{0}', {1}),".format(attribname, typestring))
            else:
                self.putln2("('{0}', {1}),".format(attribname, self.type_map[typename]))
        self.putln1("]")
        if self.packing: self.putln1("_pack_ = %u" % self.packing)
        self.type_map[structname] = structname
        self.putln1()
        self.putln1("def __init__(self, **kwargs):")
        self.putln2("super({}, self).__init__(**kwargs)".format(structname)),
        
        #self.putln2("self.freeze()")
        self.putln2("")
        
        ###################################################################
        ###################################################################
        if self.tablesSupport:
            self.printTablesSupport(members)

