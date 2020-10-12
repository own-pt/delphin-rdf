""""""

import argparse
from delphin.rdf import parser as p

from delphin.codecs import simplemrs
from delphin import itsdb
from delphin import itsdb
from delphin import tsql

from rdflib import Graph

# interface function
def cli_parse(args):
    """"""
    # validate IRI prefix
    # handle with exceptions
    # handle with invalid profile
    # handle with output exceptions

    ts = itsdb.TestSuite(args.profile)
    prefix = args.prefix.strip("/")
    graph = Graph()

    for row in tsql.select('i-id i-input mrs', ts):
        id = row[0]
        text = row[1]
        m = simplemrs.decode(row[2])
        # parse mrs from profile
        p.mrs_to_rdf(m, prefix, id, graph, text=text)
    # serializes output
    graph.serialize(destination=args.output,format=args.format)


# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=cli_parse)

# user options
# parser.add_argument("-s", "--serialize", action="store_true", help="if set, serializes the result")
parser.add_argument("profile", help="profile path")
parser.add_argument("prefix", help="valid IRI prefix")
parser.add_argument("-o", "--output", help="output file name to serialize RDF graph. Default \"output\"", default="output")
parser.add_argument("-f", "--format", help="output file format. Default \"turtle\"", default="turtle")

COMMAND_INFO = {
    'name': 'profile-to-rdf',                               # Required
    'help': 'transcribes a delphin profile to rdf format',  # Optional
    'description': __doc__,                                 # Optional
    'parser': parser,                                       # Required
}