'''
@author Mark Vismer
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import traceback
import re

if __name__ == "__main__" and __package__ is None:
    from h2pyex import *
else:
    from .support import *
    from .writer import Writer
    from .writerplus import WriterPlus
    from .writer_ctypes import WriterCTypes
    from .abstractstruct import ENDIANNESS_NETWORK


try:
    SEARCH_DIRS = os.environ['include'].split(';')
except KeyError:
    try:
        searchdirs=os.environ['INCLUDE'].split(';')
    except KeyError:
        try:
            if  sys.platform.find("beos") == 0:
                searchdirs=os.environ['BEINCLUDES'].split(';')
            elif sys.platform.startswith("atheos"):
                searchdirs=os.environ['C_INCLUDE_PATH'].split(':')
            else:
                raise KeyError
        except KeyError:
            searchdirs=['/usr/include']
            try:
                searchdirs.insert(0, os.path.join('/usr/include',
                                                  os.environ['MULTIARCH']))
            except KeyError:
                pass





def import_cheader(filename, asname=None, add_to_sys_modules=True):
    '''
    Imports a c header file as a python module.
    '''
    import imp
    from StringIO import StringIO
    out = StringIO()
    if not asname:
        assert os.path.isfile(filename)
        asname = os.path.splitext(os.path.split(filename)[1])[0]
    module = imp.new_module(asname)
    module.__dict__['__doc__'] = 'Auto-generated python module from "'+os.path.split(filename)[1]+'"'
    hr = HeaderParser(
        source=filename, output=out, errstream=None)
    hr.parse()
    exec(out.getvalue(), module.__dict__)
    if add_to_sys_modules:
        sys.modules[asname] = module
    return module





class HeaderParser(object):
    '''
    Class for parsing a c header file.
    '''

    def __init__(self, source=None, output=None, writer = None, env={}, ignores=None, default_endianness=ENDIANNESS_NETWORK, writer_cls=WriterCTypes, **kwargs):
        '''
        Constructor
        '''
        super(HeaderParser, self).__init__()

        if isstr(source):
            self.source = open(source,'r')
        else:
            self.source = source

        if writer:
            self.writer = writer
        else:
            self.writer = writer_cls(output=output, default_endianness=default_endianness)

        if kwargs.has_key('errstream'):
            self.errstream = kwargs['errstream']
            del kwargs['errstream']
        else:
            self.errstream = sys.stderr

        if kwargs: raise Exception('Unused args: ' + str(kwargs))

        self.env = env
        self.struct_format = {}

        #for k,v in TYPE_2_DEFAULTS.iteritems():
        #    exec ('{}={}\n'.format(k,v)) in self.env

        self.filedict = {}
        self.importable = {}

        #######################################################################
        #######################################################################
        self._lineno = 0

        self.current_lineno = 0

        self.current_codeline = ''

        self.last_codeline = None

        self.current_comment = ''
        self.current_inline_comment = ''
        self.last_comment = ''
        self.last_lineno = 0

        self.was_inside_comment = False
        self.was_inside_code = False


    def _put_error(self, msg):
        if not self.errstream is None:
            self.errstream.write('ERROR: ' + msg + '\n')
            self.errstream.flush()

    def next_line(self, goble_lines=True):
        '''
        Handles moving on to the next line to parse checking that the current line is
        empty (and thus parsed).
        '''

        cleaned = clean(self.current_codeline)
        if cleaned:
            self._put_error('Skipped "{}", line {}.'.format(cleaned, self.current_lineno))

        #if self.current_comment:
        #    sys.stderr.write('WARNING: Skipping comment "%s" on line %d.\n' % (self.current_comment, self.current_lineno))

        self.current_inline_comment = ''

        if self.last_codeline is not None:
            if self.last_codeline:
                self.current_codeline = self.last_codeline
                self.current_inline_comment = self.last_comment
            else:
                self.current_comment = self.last_comment
            self.last_codeline = None
            self.last_comment = ''
            self.current_lineno = self.last_lineno
            if not (self.was_inside_code or self.was_inside_comment):
                return self.current_codeline
        else:
            self.current_codeline = ''
            self.current_comment = ''

        while not self.current_codeline or ( ( self.was_inside_comment or self.was_inside_code) and not self.last_codeline):
            lineStr = self.source.readline()
            if not lineStr:
                return None
            self._lineno += 1

            if goble_lines:
                while lineStr[-2:] == '\\\n':
                    next_line = self.source.readline()
                    if not next_line:
                        raise UnexpectedException('End of file after line continuation.')
                    self._lineno += 1
                    lineStr += next_line
            elif not clean(lineStr):
                return ''

            (code, comment, self.was_inside_comment, self.was_inside_code) = \
                process_line_for_comments(lineStr, self.was_inside_comment, self.was_inside_code)
            #print((code, comment, self.was_inside_comment, self.was_inside_code))
            cleanCode =  clean(code)
            if self.current_codeline and cleanCode:
                self.last_lineno = self._lineno
                self.last_comment += comment
                self.last_codeline = clean(code)
            else:
                if cleanCode:
                    self.current_codeline += cleanCode
                    self.current_lineno = self._lineno
                if self.current_codeline:
                    self.current_inline_comment += comment
                else:
                    self.current_comment += comment
        if self.current_comment:
            fixed = self.current_comment.rstrip('\v\f\t\r\n')
            self.current_comment = fixed +'\n'
        self.current_inline_comment = clean(self.current_inline_comment)
        return self.current_codeline


    def _parse_string(self, ch):
        '''
        Searches/parses through the file for the next match of <ch>.
        '''
        while not self.current_codeline:
            self.next_line()
            if self.current_codeline is None:
                raise UnexpectedException('End of file when searching for "{}"'.format(ch))
        if not self.current_codeline.startswith(ch):
            raise ParseException('Found "{}" instead of "{}".'.format(self.current_codeline, ch), self.current_lineno)
        self.current_codeline = self.current_codeline[len(ch):]
        return self.current_codeline

    REGEX_CHAR = re.compile(r"'(\\.[^\\]*|[^\\])'")
    REGEX_HEX = re.compile(r"0x([0-9a-fA-F]+)L?")
    REGEX_U = re.compile(r"([^a-z^A-Z^_])([0-9]*)[uU]{1}")
    def pytify(self, body):
        '''
        This is a code snippet extracted from h2py.
        '''
        body = self.REGEX_CHAR.sub("ord('\\1')", body)
        body = self.REGEX_U.sub(r"\1\2", body)
        start = 0
        UMAX = 2 * (sys.maxint + 1)
        while 1:
            m = self.REGEX_HEX.search(body, start)
            if not m: break
            s, e = m.span()
            val = long(body[slice(*m.span(1))], 16)
            if val > sys.maxint:
                val -= UMAX
                body = body[:s] + "(" + str(val) + ")" + body[e:]
            start = s + 1
        return body

    REGEXT_DETECT_INCLUDE = re.compile('^[\t ]*#[\t ]*include[\t ]+<([a-zA-Z0-9_/\.]+)')
    def parse_include(self):
        '''
        This is a code snippet extracted from h2py.
        '''
        match = self.REGEXT_DETECT_INCLUDE.match(self.current_codeline)
        if match:
            regs = match.regs
            a, b = regs[1]
            filename = self.current_codeline[a:b]
            if importable.has_key(filename):
                self.writer.putln('from %s import *\n' % importable[filename])
            elif not filedict.has_key(filename):
                filedict[filename] = None
                inclfp = None
                for dir in searchdirs:
                    try:
                        inclfp = open(dir + '/' + filename)
                        break
                    except IOError:
                        pass
                if inclfp:
                    self.stderr.write('\n' +
                            '##########################################################################################' +
                            ('# Included from %s\n' % filename) +
                            '##########################################################################################' )
                    HeaderParser(inclfp, writer=self.writer, env=self.env).parse()
                    self.current_codeline = ''
                    return True
                else:
                    self._put_error('Warning - could not find file %s\n' %
                                     filename)

    REGEX_DETECT_DEFINE = re.compile(r'^[\t ]*#[\t ]*define[\t ]+([a-zA-Z0-9_]+)([\t ]+|$)')
    def parse_define(self):
        '''
        This is a code snippet extracted from h2py.
        '''
        match = self.REGEX_DETECT_DEFINE.match(self.current_codeline)
        if match:
            name = match.group(1)
            body = self.current_codeline[match.end():]
            body = self.pytify(body)
            #Need to support empty defines used as compile directives
            if not clean(body):
                body = 'None'
            stmt = '%s = %s' % (name, body.strip())
            try:
                exec(stmt, self.env)
            except:
                self._put_error("Unable to evaluate: '%s'\n  From line %d:\n\t%s\n"  % (stmt, self.current_lineno, self.current_codeline))
            else:
                self.writer.putln(stmt)
                self.current_codeline = ''
                return True

    REGEX_DETECT_MACRO = re.compile(
         r'^[\t ]*#[\t ]*define[\t ]+'
          r'([a-zA-Z0-9_]+)\(([_a-zA-Z][_a-zA-Z0-9]*)\)[\t ]+')
    def parse_macro(self):
        '''
        This is a code snippet extracted from h2py.
        '''
        match = self.REGEX_DETECT_MACRO.match(self.current_codeline)
        if match:
            macro, arg = match.group(1, 2)
            body = self.current_codeline[match.end():]
            body = self.pytify(body)
            stmt = "def %s(%s): return %s\n" % (macro, arg, body)
            try:
                exec(pythonCode, self.env)
            except:
                self._put_error(traceback.format_exc())
                raise ParseException("Could not evaluate macro '%s'." % (stmt), self.current_lineno)
            else:
                self.writer.putln(stmt)
                self.current_codeline = ''
                return True


    REGEX_DETECT_TYPDEF = re.compile(r'[\t ]*(typedef)[\t ]*([^\s.]*)[\t ]*([^\s^\[^\].]*)(\[[a-zA-Z0-9_\(\)]+\])*;')
    def parse_typedef(self):
        '''
        Tries to parse a typedef.
        '''
        success = False
        m = self.REGEX_DETECT_TYPDEF.search(self.current_codeline)
        if m:
            if 'enum' != m.group(2):
                self.writer.write_typedef(m.group(3), m.group(2),self.current_comment,self.current_lineno)
                self.current_codeline = ''
                success = True
        return success



    REGEX_DETECT_STRUCT = re.compile(r'[\t ]*(typedef)?[\t ]*struct[\t ]*([a-zA-Z0-9_\(\)]+)*')
    REGEX_DETECT_FIELD = re.compile(r'^[\t ]*([a-zA-Z0-9_]+)[\t ]+([a-zA-Z0-9_]+)[\t ]*([a-zA-Z0-9_\[\]\+\*\-\(\) \t]*?)[\t ]*;')
    REGEX_DETECT_STRUCTEND = re.compile(r'[\t ]*\}[\t ]*([a-zA-Z0-9_]*)[\t ]*;')

    def parse_struct(self):
        '''
        Tries to parse for a c struct declared as either a typedef or as
        as standalone struct with a tag.
        '''
        #TODO:F Returns:
        #TODO:F  structname - the name of the typedef or struct
        #TODO:F  fields - a list of parameters for each field

        m = self.REGEX_DETECT_STRUCT.search(self.current_codeline)
        if m:
            start_lineno = self.current_lineno
            structcomment = self.current_comment
            isTypedef = m.group(1)=='typedef'
            tagname = m.group(2)
            self.current_codeline = clean(self.current_codeline[m.end():])

            self._parse_string('{')

            ###################################################################
            ###################################################################
            members = []
            comment = ''
            m = self.REGEX_DETECT_STRUCTEND.match(self.current_codeline)
            while not m:
                self.current_codeline = clean(self.current_codeline)
                if self.current_codeline:
                    inner_match = self.REGEX_DETECT_FIELD.match(self.current_codeline)
                    if inner_match:
                        typename = inner_match.group(1)
                        (start1, end1) = inner_match.regs[1]
                        membername = inner_match.group(2)
                        (start2, end2) = inner_match.regs[2]
                        markup = inner_match.group(3)

                        #try:
                        #    # Is this a known type
                        #    unused = eval(typename +'\n', self.env)
                        #except:
                        #    try:
                        #        # Or a previously declared struct?
                        #        unused = eval(typename +'()\n', self.env)
                        #        unused
                        #    except:
                        #        raise UnsupportedDataTypeException(typename, self.current_lineno)

                        arr_match = re.match('\[(.*)\]', clean(markup))
                        if arr_match:
                            try:
                                arraysize = (eval(arr_match.group(1), self.env),)
                            except:
                                #traceback.print_exc()
                                #raise ParseException("Failed to extract array definition from '%s'" % arr_match.group(1), self.current_lineno)
                                try:
                                    arr_match = re.match('\[(.*)\]\[(.*)\]', clean(markup))
                                    if arr_match:
                                        arraysize = (eval(arr_match.group(1), self.env), eval(arr_match.group(2), self.env) )
                                    else:
                                        raise
                                except:
                                    traceback.print_exc()
                                    raise ParseException("Failed to extract array definition from '%s'" % arr_match.group(1), self.current_lineno)
                        else:
                             arraysize = None

                        if self.current_comment:
                            comment += self.current_comment
                        if self.current_inline_comment:
                            comment += self.current_inline_comment

                        members.append((membername, typename, arraysize, comment))
                        comment = ''
                        self.current_codeline = self.current_codeline[inner_match.end():]
                    else:
                        raise ParseException('Error while parsing "%s" in typedef/struct.' % self.current_codeline, self.current_lineno)
                else:
                    comment += self.current_comment

                self.current_comment = ''
                if self.next_line() is None:
                    raise UnexpectedException('End of file reached in incomplete structure definition.', start_lineno)

                m = self.REGEX_DETECT_STRUCTEND.match(self.current_codeline)

            if isTypedef:
                structname = m.group(1)
                if not structname:
                    raise ParseException("No typedef name found for struct.", start_lineno)
            else:
                structname = tagname
                if not structname:
                    raise ParseException("No tag name found for struct.", start_lineno)
            self.current_codeline = clean(self.current_codeline[m.end():])
            final_comment = self.current_comment + self.current_inline_comment

            expr = 'class %s:\n\tpass\n' % structname
            exec(expr, self.env)

            return (structname, structcomment, members, final_comment)
            #END OF if match:


    def add_expression(self, expr):
        '''
        Add a python expression to the module.
        '''
        exec(expr, self.env)
        self.writer.putln(expr.rstrip('\r\n\t '))


    def parse(self, source=None):
        '''
        Parses the input source and generates the python code.
        '''
        if source:
            if isstr(source):
                self.source = open(source,'r')
            else:
                self.source = source
        assert self.source, "No source!"
        while self.next_line(goble_lines=False) is not None:
            if self.current_codeline:
                res = self.parse_include()
                if res:
                    continue
                res = self.parse_define()
                if res:
                    continue
                res = self.parse_macro()
                if res:
                    continue
                res = self.parse_struct()
                if res:
                    self.writer.write_struct_class(*res)
                    continue
                res = self.parse_typedef()
                if res:
                    continue
                self._put_error('Skipped line %d:\n\t%s\n' % (self.current_lineno, self.current_codeline.rstrip('\r\n\t ')))
                self.current_codeline = ''

            elif self.current_comment:
                self.writer._put_comment(self.current_comment + '\n')
                self.writer.output.flush()
                self.current_comment = ''
            else:
                self.writer.putln()
                self.current_codeline = ''
        self.writer.output.flush()
        if self.errstream:
            self.errstream.flush()


if __name__ == '__main__':
    header_file = os.path.join(os.path.dirname(__file__), r'sample.h')
    output_file = os.path.join(os.path.dirname(__file__), r'sample.py');

    hr = HeaderParser(source=header_file, output=output_file)

    hr.parse()

    print('')
    print("Done!")
    #HeaderReader(hf, sys.stdout).process()


