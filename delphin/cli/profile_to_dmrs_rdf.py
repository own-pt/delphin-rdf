"""
Receives the path to a profile and attemps transcribe the texts into RDF valid format.

For more details, see: https://github.com/arademaker/delph-in-rdf.
"""

import argparse
from delphin.rdf import dmrs_to_rdf

from delphin.codecs import simplemrs
from delphin import itsdb
from delphin import tsql
from delphin import dmrs
from rdflib import Graph

# interface function
def __cli_parse__(args):
    """"""
    # validate IRI prefix
    # handle exceptions
    # handle invalid profile
    # handle output exceptions

    ts = itsdb.TestSuite(args.profile)
    prefix = args.prefix.strip("/")
    graph = Graph()

    for row in tsql.select('i-id i-input mrs', ts):
        id = row[0]
        text = row[1]
        # parse mrs from profile
        m = simplemrs.decode(row[2])
        # transform to eds:
        d = dmrs.from_mrs(m)
        if args.verbosity > 0:
            print("Parsing sentence {}".format(id))
        graph = dmrs_to_rdf(
            d=d, prefix=prefix, identifier=id,
            graph=graph, text=text)

    # serializes output
    graph.serialize(destination=args.output,format=args.format)


# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=__cli_parse__)

# user options
parser.add_argument("profile", help="profile path")
parser.add_argument("-p", dest="prefix", help="valid URI prefix (default example: http://example.com/example)", default="http://example.com/example")
parser.add_argument("--output", help="output file name to serialize RDF graph")
parser.add_argument("--format", help="output file format (default: turtle)", default="turtle")
#parser.add_argument("-v", action="store_true", help="verbose output")

COMMAND_INFO = {
    'name': 'profile-to-dmrs-to-rdf',                        # Required
    'help': 'transcribes a delphin profile to dmrs and then this to rdf format',  # Optional
    'description': __doc__,                                 # Optional
    'parser': parser,                                       # Required
}
