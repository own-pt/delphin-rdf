"""
Receives the path to a texts file or texts files container and attemps trancribe the texts into RDF valid format.

For more details, see: https://github.com/arademaker/delph-in-rdf.
"""

import os
import argparse

from delphin.rdf import textutil as util
from delphin import ace
from delphin import mrs
from rdflib import Graph

# interface function
def __cli_parse__(args):
    pass

# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=__cli_parse__)

# user options
# parser.add_argument("-s", "--serialize", action="store_true", help="if set, serializes the result")
parser.add_argument("path", help="file or directory of files containing texts to be parsed")
parser.add_argument("-p", dest="prefix", help="valid URI prefix (default example: http://example.com/example)", default="http://example.com/example")
parser.add_argument("--output", help="output file name to serialize RDF graph")
parser.add_argument("--format", help="output file format (default: turtle)", default="turtle")

COMMAND_INFO = {
    'name': 'text-to-rdf',                      # Required
    'help': 'transcribes texts to rdf format',  # Optional
    'description': __doc__,                     # Optional
    'parser': parser,                           # Required
}