"""
DOC
"""

import argparse

from delphin.rdf import parser as p
from delphin import ace
from delphin import mrs
from rdflib import Graph
# interface function
def cli_parse(args):
    print("Arguments:", args)

# set parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=cli_parse)

# user options
parser.add_argument("-s", "--serialize", action="store_true", help="if set, serializes the result")

parser.add_argument("file", help="file or directory of files containing texts to be parsed")
parser.add_argument("-o", "--output", help="output file to serialize RDF graph", default="output")
parser.add_argument("-f", "--format", help="output file format. Default \"turtle\"", default="turtle")
parser.add_argument("-g", "--grammar", help="grammar to be used by ace to parse the results")

COMMAND_INFO = {
    'name': 'text-to-rdf',              # Required
    'help': 'transcribes texts to rdf', # Optional
    'description': __doc__,             # Optional
    'parser': parser,                   # Required
}