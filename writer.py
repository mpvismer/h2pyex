"""
@author Mark Vismer
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import copy

from .support import *
from .abstractstruct import *


TYPE_TO_HDF5_MAP = {
    'bool':  'BoolCol',
    'bool_t': 'BoolCol',
    
    'char' : 'StringCol',
    
    'int8_t': 'Int8Col',
    'uint8_t':'UInt8Col',
    'int16_t':'Int16Col',
    'uint16_t':'UInt16Col',
    'int32_t':'Int32Col',
    'uint32_t':'UInt32Col',
    'int64_t':'Int64Col',
    'uint64_t':'UInt64Col',
    
    'INT8':'Int8Col',
    'UINT8':'UInt8Col',
    'INT16':'Int16Col',
    'UINT16':'UInt16Col',
    'INT32':'Int32Col',
    'UINT32':'UInt32Col',
    'INT64':'Int64Col',
    'UINT64':'UInt64Col',
    
    'float' : 'Float32Col',
    'double' : 'Float64Col',
    
    'float32_t' : 'Float32Col',
    'float64_t' : 'Float64Col'
}


TYPE_2_STRUCT_FORMAT = {
    'bool': '?',
    'bool_t': '?',
    
    'char' : 's',
    
    'int8_t':'b',
    'uint8_t':'B',
    'int16_t':'h',
    'uint16_t':'H',
    'int32_t':'i',
    'uint32_t':'I',
    'int64_t':'q',
    'uint64_t':'Q',
    
    'INT8':'b',
    'UINT8':'B',
    'INT16':'h',
    'UINT16':'H',
    'INT32':'i',
    'UINT32':'I',
    'INT64':'q',
    'UINT64':'Q',
    
    'float' : 'f',
    'double' : 'd',
    
    'float32_t' : 'f',
    'float64_t' : 'd'
}


TYPE_2_DEFAULTS = {
    'bool': 'bool',
    'bool_t': 'bool',
    
    'char' : 'str',
    
    'int8_t': 'int',
    'uint8_t': 'int',
    'int16_t': 'int',
    'uint16_t': 'int',
    'int32_t': 'int',
    'uint32_t': 'int',
    'int64_t': 'int',
    'uint64_t': 'int',
    
    'INT8': 'int',
    'UINT8': 'int',
    'INT16': 'int',
    'UINT16': 'int',
    'INT32': 'int',
    'UINT32': 'int',
    'INT64': 'int',
    'UINT64': 'int',
    
    'float' : 'float',
    'double' : 'float',
    
    'float32_t' : 'float',
    'float64_t' : 'float'
}


class Writer(object):
    """
    Creates a class for serialising and deserialising a specific c-style data structure
    python objects.
    """
    
    def __init__(self,
        output=None,
        default_endianness=ENDIANNESS_NATIVE,
        packing=1,
        indentation='    ',
        tablesSupport=True,
        type_map=TYPE_2_STRUCT_FORMAT,
        defaults_map=TYPE_2_DEFAULTS):
        """
        Constructor
        """
        super(Writer, self).__init__()
        self.type_map = copy.deepcopy(type_map)
        self.defaults_map = copy.deepcopy(defaults_map)
        self.hdf5_map = copy.deepcopy(TYPE_TO_HDF5_MAP)
        self.has_dependencies = False
        if output is None:
            self.output = sys.stdout
        elif isstr(output):
            self.output = open(output,'w')
        else:
            self.output = output
        self.indentation = indentation
        self.default_endianness = default_endianness
        self.packing = packing
        self.tablesSupport=tablesSupport
        #self.putln("from __future__ import unicode_literals")
    
    
    def _format_comment_block(self, comment, indentation_count=0):
        """
        Applies indentation to the lines of a comment block.
        """
        lines = comment.splitlines()
        output = ''
        for line in lines:
            output += self.indentation*indentation_count
            output += '# ' + line.strip() + '\n'
        return output
    
    
    def _format_string_block(self, text, indentation_count=0):
        """
        Applies indentation to the lines of a string.
        """
        lines = text.splitlines()
        prefix = self.indentation*indentation_count
        return prefix + ('\n' + prefix).join(lines) + '\n'
    
    
    def _put_comment(self, comment, indentation_count=0):
        """
        Prints out the comment block with correct formatting.
        """
        self.output.write(self._format_comment_block(comment, indentation_count))
    
    def put_doc_comment(self, doc_comment, indentation_count=0):
        """
        Formats and prints out a docstring.
        """
        self.output.write(self.indentation*indentation_count + "'''\n")
        self.output.write(self._format_string_block(doc_comment.rstrip(), indentation_count))
        self.output.write(self.indentation*indentation_count + "'''\n")
    
    def putln(self, line=""):
        self.output.write(line + "\n")
    
    def putln1(self, line=""):
        self.output.write(self.indentation + line + "\n")
    
    def putln2(self, line=""):
        self.output.write(self.indentation*2 + line + "\n")
    
    def putln3(self, line=""):
        self.output.write(self.indentation*3 + line + "\n")
    
    
    def _check_dependencies(self):
        """
        Adds dependencies for custom struct classes (if not already present).
        """
        if not self.has_dependencies:
            #self.putln("# For python 3 compatibility")
            #self.putln("from __future__ import absolute_import")
            #self.putln("from __future__ import division")
            #self.putln("from __future__ import print_function")
            #self.putln("from __future__ import unicode_literals")
            #self.putln()
            self.putln("# Support for structure types.")
            self.putln('import struct')
            self.putln('import copy')
            self.putln('import string')
            self.putln('from h2pyex import AbstractStruct, utils')
            self.putln()
            self.has_struct_dependencies = True
    
    
    def write_typedef(self, defname, typename, comment, lineno):
        """
        Writes a typedef to the output file.
        """
        try :
            actualtype = self.type_map[typename]
            actualhdf5type = self.hdf5_map[typename]
        except:
            raise UnsupportedDataTypeException("For {} on line {}.".format(typename, lineno))
        else:
            self.type_map[defname] = actualtype
            self.hdf5_map[defname] = actualtype
        self._check_dependencies()
        self._put_comment(comment, 1)
        self.putln("{} = '{}'".format(defname, actualtype))
    
    
    def write_struct_class(self, structname, comment, members, final_comment=''):
        """
        Writes the python code for a class to serialise/deserialise a structure.
        """
        self._check_dependencies()
        self.putln("class {}(AbstractStruct):".format(structname))
        self.put_doc_comment(comment, 1)
        
        self.putln1('_fields_ = [')
        for (attribname, typename, dimensions, comment) in members:
            if not dimensions:
                self.putln3("('{}', '{}'),".format(attribname, typename))
            else:
                typestring = typename
                for dim in reversed(dimensions):
                    typestring = '{}*{}'.format(typestring, dim)
                self.putln3("('{}', '{}'),".format(attribname,typestring))
        self.putln2(']')
        self.putln1()
        
        #######################################################################
        #######################################################################
        self.putln1("def __init__(self,")
        self.putln3("endianness='{}',".format(self.default_endianness))
        self.putln3("**kwargs):"),
        self.putln2("super({}, self).__init__()".format(structname)),
        
        
        #  if comment:
#           #self.output.write(3*INDENT + '# ' + comment.rstrip('\r\n\t ') + '\n' )
                #self.printComment(comment.rstrip('\r\n\t '), 3*self.indentation)
        
        
        #fmt = '{}'.format(self.default_endianness)
        fmt = ''
        struct_classes = []
        for (attribname, typename, dimensions, comment) in members:
            if dimensions:
                try:
                    formatstring = self.type_map[typename]
                    defaultstring = self.defaults_map[typename]
                    if 's'==formatstring:
                        formatstring = '{}{}'.format(dimensions[-1], formatstring)
                        dimensions = dimensions[:-1]
                except KeyError:
                    formatstring = ''
                    struct_classes.append((typename, dimensions))
                    defaultstring = typename
                tot_len = 1
                for dim in dimensions:
                    tot_len = tot_len*dim
                formatstring = formatstring*tot_len
                self.putln2("self._struct_{0} = struct.Struct(str(endianness + '{1}'))".format(attribname, formatstring))
                self.putln2("self.{} = utils.array_unflatten([{}() for idx in range(0,{})], {})".format(attribname, defaultstring, tot_len, repr(dimensions)))
                self.putln2("if '{}' in kwargs:".format(attribname))
                self.putln2("    setattr(self, '{0}', kwargs.pop('{0}'))".format(attribname))
            else:
                try:
                    formatstring = self.type_map[typename]
                    typename = self.defaults_map[typename]
                    self.putln2("self._struct_{0} = struct.Struct(str(endianness + '{1}'))".format(attribname, formatstring))
                except KeyError:
                    formatstring = ''
                    struct_classes.append((typename, None))
                self.putln2("setattr(self, '{0}', kwargs.pop('{0}', {1}()))".format(attribname, typename))
            fmt+= formatstring
        
        self.putln2("if kwargs: raise Exception('Unused args: ' + str(kwargs))")
        self.putln2("self._endianness = endianness")
        self.putln2("# Note that if there are nested structs, self._packing_struct is incomplete")
        self.putln2("# and just used for calculating the packed size.")
        self.putln2("self._packing_format = endianness + '{}'".format(fmt))
        self.putln2("self._packing_struct = struct.Struct(str(self._packing_format))")
        
        self.putln2("self._packed_size = self._packing_struct.size")
        if struct_classes:
            for cls, dims in struct_classes:
                cnt = 1
                if dims is not None:
                    for dim in dims:
                        cnt *= dim
                self.putln2("self._packed_size += {}().packed_size()*{}".format(cls, cnt))
        
        self.putln2("self.freeze()")
        self.putln2("")
        
        ###################################################################
        ###################################################################
        self.putln1("def serialise(self):")
        if len(struct_classes)==0:
            self.putln2("return self._packing_struct.pack( *(\\")
            for (attribname, typename, dimensions, comment) in members:
                if dimensions:
                    self.putln3("utils.array_flatten(self.{}) + \\".format(attribname))
                else:
                    self.putln3("[self.{}] + \\".format(attribname))
            self.putln3("[] ))")
        else:
            self.putln2("data = []")
            for (attribname, typename, dimensions, comment) in members:
                try:
                    struct_format = self.type_map[typename]
                    if dimensions:
                        self.putln2("data.append(self._struct_{0}.pack(*utils.array_flatten(self.{0})))".format(attribname))
                    else:
                        self.putln2("data.append(self._struct_{0}.pack(self.{0}))".format(attribname))
                except KeyError:
                    if dimensions:
                        self.putln2("for element in utils.array_flatten(self.{}):".format(attribname) )
                        self.putln3(    "data.append(element.serialise())")
                    else:
                        self.putln2("data.append(self.{0}.serialise())".format(attribname))
            self.putln2("return b''.join(data)")
        self.putln2("")
        
        ###################################################################
        ###################################################################
        self.putln1("def deserialise_from(self, buf, offset):")
        if len(struct_classes)==0:
            self.putln2("results = self._packing_struct.unpack_from(buf, offset)")
            idx = 0;
            for (attribname, typename, dimensions, comment) in members:
                if dimensions:
                    if 's' == self.type_map[typename]:
                        dimensions = dimensions[:-1]
                    arraysize = 1
                    for dim in dimensions:
                        arraysize *= dim
                    self.putln2("self.{} = utils.array_unflatten(results[{}:{}],{})".format(attribname, idx, idx+arraysize, repr(dimensions)))
                    idx+=arraysize
                else:
                    self.putln2("self.{} = results[{}]".format(attribname, idx))
                    idx+=1
        else:
            for (attribname, typename, dimensions, comment) in members:
                if typename in self.type_map:
                    if dimensions:
                        if 's' == self.type_map[typename]:
                            dimensions = dimensions[:-1]
                        self.putln2("self.{0} = utils.array_unflatten(self._struct_{0}.unpack_from(buf, offset),{1})".format(attribname, repr(dimensions)))
                    else:
                        self.putln2("(self.{0},) = self._struct_{0}.unpack_from(buf, offset)".format(attribname))
                    self.putln2("offset += self._struct_{0}.size".format(attribname))
                else:
                    if dimensions:
                        self.putln2("for element in utils.array_flatten(self.{}):".format(attribname) )
                        self.putln2("    element.deserialise_from(buf, offset)")
                        self.putln2("    offset += element.packed_size()")
                    else:
                        self.putln2("self.{0}.deserialise_from(buf, offset)".format(attribname))
                        self.putln2("offset += self.{0}.packed_size()".format(attribname))
        
        ###################################################################
        ###################################################################
        if self.tablesSupport:
            self.printTablesSupport(members)
        
        ###################################################################
        ###################################################################
        if final_comment:
            self.putln(self._format_comment_block(final_comment, 1))
        self.putln("\n")
    
    
    def printTablesSupport(self, members):
        """
        Writes out the make_table_descriptor function.
        """
        self.putln()
        self.putln1("def make_table_descriptor(self):")
        self.putln1("    import tables")
        self.putln1("    class TableRow(tables.IsDescription):")
        self.putln1("        time = tables.Float32Col(pos=1)")
        for i, (attribname, typename, dimensions, comment) in enumerate(members):
            try:
                hdf5type = self.hdf5_map[typename]
                if dimensions:
                    self.putln3("{} = tables.{}(pos={}, shape={})".format(attribname, hdf5type, i+2, repr(dimensions)))
                else:
                    self.putln3("{} = tables.{}(pos={})".format(attribname, hdf5type, i+2))
            except KeyError:
                self.putln3("{0} = self.{0}.make_table_descriptor()".format(attribname))
        self.putln2("return TableRow")
        self.putln3()
