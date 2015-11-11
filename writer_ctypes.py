'''
@author Mark Vismer
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ctypes import *

from .writer import *


TYPE_2_CTYPE_MAP = {
    'bool'      : c_bool,
    'bool_t'    : c_bool,

    'int8_t'    : c_byte,
    'uint8_t'   : c_ubyte,
    'int16_t'   : c_short,
    'uint16_t'  : c_ushort,
    'int32_t'   : c_long,
    'uint32_t'  : c_ulong,
    'int64_t'   : c_longlong,
    'uint64_t'  : c_ulonglong,

    'INT8'      : c_byte,
    'UINT8'     : c_ubyte,
    'INT16'     : c_short,
    'UINT16'    :  c_ushort,
    'INT32'     : c_long,
    'UINT32'    : c_ulong,
    'INT64'     : c_longlong,
    'UINT64'    : c_ulonglong,

    'float'     : c_float,
    'double'    :  c_double,

    'float32_t' : c_float,
    'float64_t' : c_double
}

TYPE_2_CTYPESTR_MAP = {
    'bool'      : 'c_bool',
    'bool_t'    : 'c_bool',

    'int8_t'    : 'c_byte',
    'uint8_t'   : 'c_ubyte',
    'int16_t'   : 'c_short',
    'uint16_t'  : 'c_ushort',
    'int32_t'   : 'c_long',
    'uint32_t'  : 'c_ulong',
    'int64_t'   : 'c_longlong',
    'uint64_t'  : 'c_ulonglong',

    'INT8'      : 'c_byte',
    'UINT8'     : 'c_ubyte',
    'INT16'     : 'c_short',
    'UINT16'    : 'c_ushort',
    'INT32'     : 'c_long',
    'UINT32'    : 'c_ulong',
    'INT64'     : 'c_longlong',
    'UINT64'    : 'c_ulonglong',

    'float'     : 'c_float',
    'double'    : 'c_double',

    'float32_t' : 'c_float',
    'float64_t' : 'c_double'
}


ENDIANNESS_MAP = {
    ENDIANNESS_NETWORK : 'BigEndianStructure',
    ENDIANNESS_BIG:'BigEndianStructure',
    ENDIANNESS_LITTLE:'LittleEndianStructure',
    ENDIANNESS_NATIVE:'Structure'
    }

class WriterCTypes(Writer):
    '''
    A modified verson of Writer to create a class where ctypes are used.
    '''
    def __init__(self, **kwargs):
        super(WriterCTypes, self).__init__(type_map=TYPE_2_CTYPESTR_MAP, **kwargs)

    def _check_dependencies(self):
        if not self.has_dependencies:
            self.putln("from ctypes import *")
            self.putln("from h2pyex.ctypesstruct import CTypesStruct")
            self.has_dependencies = True

    def write_struct_class(self, structname, structcomment, members, final_comment=''):
        self._check_dependencies()
        self.putln("class {}(CTypesStruct, {}):".format(structname, ENDIANNESS_MAP[self.default_endianness]))
        self._put_comment(structcomment,1)
        self._put_comment(final_comment,1)
        self.putln1("_fields_ = [")
        for (attribname, typename, dimensions, comment) in members:
            if dimensions is not None:
                typestring = self.type_map[typename]
                for dim in reversed(dimensions):
                    typestring = '({}*{})'.format(typestring, dim)
                self.putln2("('{0}', {1}),".format(attribname, typestring))
            else:
                self.putln2("('{0}', {1}),".format(attribname, self.type_map[typename]))
        self.putln1("]")
        self.putln1("_pack_ = %u"%self.packing)
        self.type_map[structname] = structname
        self.putln1()
        self.putln1("def __init__(self, **kwargs):")
        self.putln2("super({}, self).__init__(**kwargs)".format(structname)),

        self.putln2("self.freeze()")
        self.putln2("")

        ###################################################################
        ###################################################################
        if self.tablesSupport:
            self.printTablesSupport(members)

