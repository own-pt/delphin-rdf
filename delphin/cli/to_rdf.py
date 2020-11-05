"""
Receives an input and attemps trancribe the texts into RDF valid format.

For more details, see: https://github.com/arademaker/delph-in-rdf.
"""

import os, sys
import argparse
from delphin.rdf import mrs_to_rdf
from delphin.codecs import simplemrs
from rdflib import Graph

# interface function
def __cli_parse__(args):
    """"""

    print(args)

    fmt = args.fmt
    path = args.path
    pref = args.prefix
    idtf = args.identifier
    
    # if a testsuite dir
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()
    elif os.path.isdir(path):
        path = path.strip("/")+"/result.mrs"
        input_text = open(path, "r").read()

    if fmt == "simplemrs":
        m = simplemrs.decode(input_text)
        g = mrs_to_rdf(m, pref, idtf)
    elif fmt == "eds":
        pass
    elif fmt == "simpledmrs":
        pass
    # dmrsjson, dmrspenman, dmrx, edsjson, edspenman
    # indexedmrs, mrsjson, mrsprolog, mrx
    else: raise ValueError("No a valid format given")

    print(g.serialize(args.output, None))

# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=__cli_parse__)

# user options
parser.add_argument("path", nargs="*", help="file with representations to convert; if not given, <stdin> is read as though it were a file", default=sys.stdin)
parser.add_argument("-f", "--from", dest="fmt", help="original representation (default: simplemrs)", default="simplemrs")
parser.add_argument("-p", dest="prefix", help="valid URI prefix. Example: \"http://example.com/example\"", default="http://example.com/example")
parser.add_argument("-i", dest="identifier", help="an string identifying the mrs (default: 0)", default="0")
parser.add_argument("--output", help="output file name to serialize RDF graph")
parser.add_argument("--format", help="output file format (default: turtle)", default="turtle")

COMMAND_INFO = {
    'name': 'to-rdf',                               # Required
    'help': 'transcribes an input into rdf format', # Optional
    'description': __doc__,                         # Optional
    'parser': parser,                               # Required
}