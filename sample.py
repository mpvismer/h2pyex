SAMPLE_H = None


import struct
from h2pyex.abstractstruct import AbstractStruct
class Sample_StructDef_t(AbstractStruct):
    
    def __init__(self,
            endianness='!',
            **kwargs):
        self._struct_bi = struct.Struct(str(endianness + 'b'))
        self.bi = kwargs.get('bi', 0)
        if kwargs.has_key('bi'): del kwargs['bi']
        self._struct_bu = struct.Struct(str(endianness + 'B'))
        self.bu = kwargs.get('bu', 0)
        if kwargs.has_key('bu'): del kwargs['bu']
        self._struct_di = struct.Struct(str(endianness + 'h'))
        self.di = kwargs.get('di', 0)
        if kwargs.has_key('di'): del kwargs['di']
        self._struct_du = struct.Struct(str(endianness + 'H'))
        self.du = kwargs.get('du', 0)
        if kwargs.has_key('du'): del kwargs['du']
        self._struct_qi = struct.Struct(str(endianness + 'i'))
        self.qi = kwargs.get('qi', 0)
        if kwargs.has_key('qi'): del kwargs['qi']
        self._struct_qu = struct.Struct(str(endianness + 'I'))
        self.qu = kwargs.get('qu', 0)
        if kwargs.has_key('qu'): del kwargs['qu']
        self._struct_f = struct.Struct(str(endianness + 'f'))
        self.f = kwargs.get('f', 0.0)
        if kwargs.has_key('f'): del kwargs['f']
        self._struct_dbl = struct.Struct(str(endianness + 'd'))
        self.dbl = kwargs.get('dbl', 0.0)
        if kwargs.has_key('dbl'): del kwargs['dbl']
        if kwargs: raise Exception('Unused args: ' + str(kwargs))
        self._endianness = endianness
        self._packingFormat = endianness + 'bBhHiIfd'
        self._packing_struct = struct.Struct(str(self._packingFormat))
        self._packed_size = self._packing_struct.size
        self.freeze()
        
    def serialise(self):
        return self._packing_struct.pack( *(\
            [self.bi] + \
            [self.bu] + \
            [self.di] + \
            [self.du] + \
            [self.qi] + \
            [self.qu] + \
            [self.f] + \
            [self.dbl] + \
            [] ))
        
    def deserialise_from(self, buf, offset):
        results = self._packing_struct.unpack_from(buf, offset)
        self.bi = results[0]
        self.bu = results[1]
        self.di = results[2]
        self.du = results[3]
        self.qi = results[4]
        self.qu = results[5]
        self.f = results[6]
        self.dbl = results[7]


class Sample_StructDefArrays_t(AbstractStruct):
    
    def __init__(self,
            endianness='!',
            **kwargs):
        self._struct_bi = struct.Struct(str(endianness + 'bbbbb'*5))
        self.bi = kwargs.get('bi', 5*[0])
        assert 5==len(self.bi), "Attribute 'bi' has invalid length."
        if kwargs.has_key('bi'): del kwargs['bi']
        self._struct_bu = struct.Struct(str(endianness + 'BBB'*3))
        self.bu = kwargs.get('bu', 3*[0])
        assert 3==len(self.bu), "Attribute 'bu' has invalid length."
        if kwargs.has_key('bu'): del kwargs['bu']
        self._struct_di = struct.Struct(str(endianness + 'hh'*2))
        self.di = kwargs.get('di', 2*[0])
        assert 2==len(self.di), "Attribute 'di' has invalid length."
        if kwargs.has_key('di'): del kwargs['di']
        self._struct_du = struct.Struct(str(endianness + 'H'))
        self.du = kwargs.get('du', 0)
        if kwargs.has_key('du'): del kwargs['du']
        self._struct_qi = struct.Struct(str(endianness + ''*0))
        self.qi = kwargs.get('qi', 0*[0])
        assert 0==len(self.qi), "Attribute 'qi' has invalid length."
        if kwargs.has_key('qi'): del kwargs['qi']
        self._struct_qu = struct.Struct(str(endianness + 'I'*1))
        self.qu = kwargs.get('qu', 1*[0])
        assert 1==len(self.qu), "Attribute 'qu' has invalid length."
        if kwargs.has_key('qu'): del kwargs['qu']
        self._struct_f = struct.Struct(str(endianness + 'ffff'*4))
        self.f = kwargs.get('f', 4*[0.0])
        assert 4==len(self.f), "Attribute 'f' has invalid length."
        if kwargs.has_key('f'): del kwargs['f']
        self._struct_dbl = struct.Struct(str(endianness + 'ddd'*3))
        self.dbl = kwargs.get('dbl', 3*[0.0])
        assert 3==len(self.dbl), "Attribute 'dbl' has invalid length."
        if kwargs.has_key('dbl'): del kwargs['dbl']
        if kwargs: raise Exception('Unused args: ' + str(kwargs))
        self._endianness = endianness
        self._packingFormat = endianness + 'bbbbbBBBhhHIffffddd'
        self._packing_struct = struct.Struct(str(self._packingFormat))
        self._packed_size = self._packing_struct.size
        self.freeze()
        
    def serialise(self):
        return self._packing_struct.pack( *(\
            list(self.bi) + \
            list(self.bu) + \
            list(self.di) + \
            [self.du] + \
            list(self.qi) + \
            list(self.qu) + \
            list(self.f) + \
            list(self.dbl) + \
            [] ))
        
    def deserialise_from(self, buf, offset):
        results = self._packing_struct.unpack_from(buf, offset)
        self.bi = results[0:5]
        self.bu = results[5:8]
        self.di = results[8:10]
        self.du = results[10]
        self.qi = results[11:11]
        self.qu = results[11:12]
        self.f = results[12:16]
        self.dbl = results[16:19]


class Sample_NestC_t(AbstractStruct):
    
    def __init__(self,
            endianness='!',
            **kwargs):
        self._struct_afloat = struct.Struct(str(endianness + 'f'))
        self.afloat = kwargs.get('afloat', 0.0)
        if kwargs.has_key('afloat'): del kwargs['afloat']
        if kwargs: raise Exception('Unused args: ' + str(kwargs))
        self._endianness = endianness
        self._packingFormat = endianness + 'f'
        self._packing_struct = struct.Struct(str(self._packingFormat))
        self._packed_size = self._packing_struct.size
        self.freeze()
        
    def serialise(self):
        return self._packing_struct.pack( *(\
            [self.afloat] + \
            [] ))
        
    def deserialise_from(self, buf, offset):
        results = self._packing_struct.unpack_from(buf, offset)
        self.afloat = results[0]


class Sample_NestB_t(AbstractStruct):
    
    def __init__(self,
            endianness='!',
            **kwargs):
        self._struct_afloat = struct.Struct(str(endianness + 'f'))
        self.afloat = kwargs.get('afloat', 0.0)
        if kwargs.has_key('afloat'): del kwargs['afloat']
        self.cnests = kwargs.get('cnests', Sample_NestC_t())
        if kwargs.has_key('cnests'): del kwargs['cnests']
        if kwargs: raise Exception('Unused args: ' + str(kwargs))
        self._endianness = endianness
        self._packingFormat = endianness + 'f'
        self._packing_struct = struct.Struct(str(self._packingFormat))
        self._packed_size = self._packing_struct.size
        self._packed_size += Sample_NestC_t().packed_size()*1
        self.freeze()
        
    def serialise(self):
        data = []

        data.append(self._struct_afloat.pack(self.afloat))
        data.append(self.cnests.serialise())
        return ''.join(data)
        
    def deserialise_from(self, buf, offset):
        (self.afloat,) = self._struct_afloat.unpack_from(buf, offset)
        offset += self._struct_afloat.size
        self.cnests.deserialise_from(buf, offset)
        offset += self.cnests.packed_size()


class Sample_NestA_t(AbstractStruct):
    
    def __init__(self,
            endianness='!',
            **kwargs):
        self.bnest = kwargs.get('bnest', Sample_NestB_t())
        if kwargs.has_key('bnest'): del kwargs['bnest']
        self._struct_testdouble = struct.Struct(str(endianness + 'd'))
        self.testdouble = kwargs.get('testdouble', 0.0)
        if kwargs.has_key('testdouble'): del kwargs['testdouble']
        self.cnest = kwargs.get('cnest', Sample_NestC_t())
        if kwargs.has_key('cnest'): del kwargs['cnest']
        self.bnests = kwargs.get('bnests', [Sample_NestB_t() for _ in range(2)])
        assert 2==len(self.bnests), "Attribute 'bnests' has invalid length."
        if kwargs.has_key('bnests'): del kwargs['bnests']
        if kwargs: raise Exception('Unused args: ' + str(kwargs))
        self._endianness = endianness
        self._packingFormat = endianness + 'd'
        self._packing_struct = struct.Struct(str(self._packingFormat))
        self._packed_size = self._packing_struct.size
        self._packed_size += Sample_NestB_t().packed_size()*1
        self._packed_size += Sample_NestC_t().packed_size()*1
        self._packed_size += Sample_NestB_t().packed_size()*2
        self.freeze()
        
    def serialise(self):
        data = []

        data.append(self.bnest.serialise())
        data.append(self._struct_testdouble.pack(self.testdouble))
        data.append(self.cnest.serialise())
        for element in self.bnests:
            data.append(element.serialise())
        return ''.join(data)
        
    def deserialise_from(self, buf, offset):
        self.bnest.deserialise_from(buf, offset)
        offset += self.bnest.packed_size()
        (self.testdouble,) = self._struct_testdouble.unpack_from(buf, offset)
        offset += self._struct_testdouble.size
        self.cnest.deserialise_from(buf, offset)
        offset += self.cnest.packed_size()
        for element in self.bnests:
            element.deserialise_from(buf, offset)
            offset += element.packed_size()


