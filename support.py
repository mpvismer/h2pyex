"""
@author Mark Vismer
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import re

_path = os.path.realpath(os.path.abspath(os.path.join(__file__,'../../../Python')))
sys.path.append(_path)
try:
    import pyutils as utils
    from pyutils import isstr, enum_fields
except ImportError as e:
    import utils
    from utils import isstr, enum_fields

try:
    from .userexceptions import *
except:
    from userexceptions import *


def clean(s):
    """ Remove white spaces from <s>. """
    return s.strip(' \t\n\r\f\v')


COMMENT_START_REGEX = re.compile(r'((///?)|(/\*\*?)|(\"))')

def process_line_for_comments(line, inside_comment=False, inside_string=False):
    """
    Processes a line of a c file to extract a comment.
    """
    comment = ''
    code = ''
    while line:
        if inside_comment:
            #  Inside a comment!
            idx = line.find('*/')
            if idx>=0:
                comment += line[:idx]
                line = line[idx+2:]
                inside_comment = False
            else:
                comment += line
                #line = ''
                break
        elif inside_string:
            idx = line.find('"')
            if idx < 0:
                if not line.endswith('\\'):
                    print(line)
                    print(code)
                    print(comment)
                    raise ParseException("Mal formed c-string.")
                code += line + '\n'
                #line = ''
                break
            else:
                inside_string = False
                code += line[:idx] + '"""'
                line = line[idx+1:]
        else:
            m = COMMENT_START_REGEX.search(line)
            if m:
                if m.group(1) == '"':
                    inside_string = True
                    end = m.end()
                    code += '"""' + line[:(end-1)]
                    line = line[end:]
                else:
                    code += line[:m.start()]
                    if m.group(1).startswith('/*'):
                        line = line[m.end():]
                        inside_comment = True
                    else:
                        comment += line[m.end():]
                        #line = ''
                        break
            else:
                code += line
                break
    
    return code, comment, inside_comment, inside_string


