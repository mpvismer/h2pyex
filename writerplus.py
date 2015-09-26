'''
@author Mark Vismer
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from .writer import *



class WriterPlus(Writer):
    '''
    A modified version of Writer to create a class where the Endianness is
    associated with the class type therefore not stored with each instance.
    '''

    def write_struct_class(self, structname, comment, members, final_comment=''):
        '''
        Writes the python code for a class to serialise/deserialise a structure.
        '''

        self._check_dependencies()

        self.putln("class {}(AbstractStruct):".format(structname))
        self.putln1("'''")
        self.putln1(self._format_comment_block(comment, 1))
        self.putln1("'''")
        self.putln1()

        self.putln1('_fields_ = [')
        for (attribname, typename, arraysize, comment) in members:
            if arraysize>=0:
                self.putln3("('{}', '{}*{}'),".format(attribname, typename, arraysize))
            else:
                self.putln3("('{}', '{}'),".format(attribname, typename))
        self.putln2(']')
        self.putln1()


        #######################################################################


        #######################################################################
        self.putln1("@classmethod")
        self.putln1("def setEndianness(cls, endianness):")
        self.putln2("''' Sets the Endianness of the actual underlying class type.'''")

        fmt = ''
        struct_classes = []
        for (attribname, typename, arraysize, comment) in members:

            if arraysize<0:
                arraysize = 1
            try:
                struct_format = self.type_map[typename]*arraysize
                fmt+= struct_format



                self.putln2("cls._struct_{0} = struct.Struct(str(endianness + '{1}'*{2}))".format(attribname, struct_format, arraysize))
            except KeyError:

                struct_classes.append((typename, arraysize))
                pass


        self.putln2("# Note that if there are nested structs, _packing_struct is")
        self.putln2("# incomplete and just used for calculating the packed size.")
        self.putln2("cls._packingFormat = endianness + '{}'".format(fmt))

        self.putln2("cls._packing_struct = struct.Struct(str(cls._packingFormat))")

        self.putln2("cls._packed_size = cls._packing_struct.size")
        if struct_classes:
            for cls, cnt in struct_classes:
                self.putln2("cls._packed_size += {}().packed_size()*{}".format(cls, cnt))
        self.putln2("return cls")
        self.putln2()

        #######################################################################

        #######################################################################
        self.putln1("def __init__(self,")
        self.putln3("**kwargs):"),







        #  if comment:
#           #self.outFile.write(3*INDENT + '# ' + comment.rstrip('\r\n\t ') + '\n' )
                #self.printComment(comment.rstrip('\r\n\t '), 3*self.indentation)



        for (attribname, typename, arraysize, comment) in members:
            if arraysize>=0:
                try:
                    defaultvalue = self.defaults_map[typename]



                    self.putln2("self.{0} = kwargs.get('{0}', {1}*[{2}])".format(attribname, arraysize, defaultvalue))
                except KeyError:
                    self.putln2("self.{0} = kwargs.get('{0}', [{1}() for _ in range({2})])".format(attribname, typename, arraysize))
                self.putln2('''assert {0}==len(self.{1}), "Attribute '{1}' has invalid length."'''.format(arraysize, attribname, attribname))
            else:
                try:
                    defaultvalue = self.defaults_map[typename]
                    self.putln2("self.{0} = kwargs.get('{0}', {1})".format(attribname, defaultvalue))
                except KeyError:
                    self.putln2("self.{0} = kwargs.get('{0}', {1}())".format(attribname, typename))
            self.putln2("if kwargs.has_key('{0}'): del kwargs['{0}']".format(attribname))
        self.putln2("if kwargs: raise Exception('Unused args: ' + str(kwargs))")

        self.putln2("self.freeze()")
        self.putln2("")

        ###################################################################

        ###################################################################
        self.putln1("def serialise(self):")
        if len(struct_classes)==0:


            self.putln2("return self._packing_struct.pack( *(\\")
            for (attribname, typename, arraysize, comment) in members:
                if arraysize>=0:
                    self.putln3("list(self.{}) + \\".format(attribname))
                else:
                    self.putln3("[self.{}] + \\".format(attribname))
            self.putln3("[] ))")
        else:
            self.putln2("data = []\n")
            for (attribname, typename, arraysize, comment) in members:
                try:

                    struct_format = self.type_map[typename]


                    if arraysize==0:
                        print("Attribute %s has array size of 0 and was omitted." % attribname)
                    if arraysize>=0:
                        self.putln2("data.append(self._struct_{0}.pack(*self.{0}))".format(attribname))
                    else:
                        self.putln2("data.append(self._struct_{0}.pack(self.{0}))".format(attribname))
                except KeyError:
                    if arraysize>=0:
                        self.putln2("for element in self.{}:".format(attribname) )
                        self.putln3(    "data.append(element.serialise())")
                    else:
                        self.putln2("data.append(self.{0}.serialise())".format(attribname))
            self.putln2("return ''.join(data)")
        self.putln2("")

        ###################################################################

        ###################################################################
        self.putln1("def deserialise_from(self, buf, offset):")
        if len(struct_classes)==0:


            self.putln2("results = self._packing_struct.unpack_from(buf, offset)")
            idx = 0;
            for (attribname, typename, arraysize, comment) in members:
                if arraysize>=0:
                    self.putln2("self.{} = results[{}:{}]".format(attribname, idx, idx+arraysize))
                    idx+=arraysize
                else:
                    self.putln2("self.{} = results[{}]".format(attribname, idx))
                    idx+=1
        else:
            for (attribname, typename, arraysize, comment) in members:
                try:
                    field_format = self.type_map[typename]
                    if arraysize>=0:
                        self.putln2("self.{0} = self._struct_{0}.unpack_from(buf, offset)".format(attribname))
                    else:
                        self.putln2("(self.{0},) = self._struct_{0}.unpack_from(buf, offset)".format(attribname))
                    self.putln2("offset += self._struct_{0}.size".format(attribname))
                except KeyError:
                    if arraysize>=0:
                        self.putln2("for element in self.{}:".format(attribname) )
                        self.putln2("    element.deserialise_from(buf, offset)")
                        self.putln2("    offset += element.packed_size()")
                    else:
                        self.putln2("self.{0}.deserialise_from(buf, offset)".format(attribname))
                        self.putln2("offset += self.{0}.packed_size()".format(attribname))

        ###################################################################

        ###################################################################
        if final_comment:
            self.putln(self._format_comment_block(final_comment, 1))


        self.putln("{}.setEndianness('{}')".format(structname, self.default_endianness))
        self.putln("\n")


