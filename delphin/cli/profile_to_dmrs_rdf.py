"""
Transcribes an profile intro a DMRS-RDF graph.

For more details, see: {https://github.com/arademaker/delph-in-rdf}.
"""

from os.path import isdir

import argparse
import warnings
import logging
logger = logging.getLogger(__name__)

# from progress.bar import Bar as ProgressBar

from delphin.exceptions import PyDelphinException, PyDelphinWarning
from delphin.tsdb import TSDBError, TSDBWarning

from delphin.rdf import dmrs_to_rdf

from delphin.codecs import simplemrs
from delphin.tsdb import is_database_directory
from delphin.mrs import is_well_formed
from delphin.dmrs import from_mrs
from delphin import itsdb
from delphin import tsql

from rdflib import Graph
from rdflib.term import _is_valid_uri

# interface function
def __cli_parse__(args):
    # remove the not well formed sentences? add option?
    # print MRS or parse to DMRS format?

    graph = Graph()
    path = args.profile
    prefix = args.prefix.strip("/")
    
    try:
        # validates path
        if not isdir(path):
            raise NotADirectoryError(f"Path is not a directory: {path}")
        # validates profile
        if not is_database_directory(path):
            raise TSDBError(f'Invalid test suite directory: {path}')
        # validates URI prefix
        if not _is_valid_uri(prefix):
            raise Exception(f'Invalid URI: {prefix}')
        
        # open Test Suite and start conversion
        ts = itsdb.TestSuite(path)
        items = len(ts['item'])
        logger.info(f"Converting {items} items from {args.profile}")

        for row in tsql.select('i-id i-input mrs', ts):
            id = row[0]
            text = row[1]
            encoded = row[2]
            m = simplemrs.decode(encoded)

            # making sure of the well formedness of "m"
            if not is_well_formed(m):
                logger.warning(f"Item {id} not well formed.")
                # continue

            # parse mrs to dmrs and parse it
            d = from_mrs(m)
            logger.debug(f"Item {id}: \n\t{text}\n\t{d}\n\t{encoded}")
            
            graph = dmrs_to_rdf(
                        d=d,
                        prefix=prefix,
                        identifier=id,
                        graph=graph,
                        text=text)

        # serializes results
        logger.info(f"Serializing results to {args.output}.")
        graph.serialize(destination=args.output, format=args.format)
        logger.info(f"DONE.")

    # except PyDelphinSyntaxError as e:
    #     logger.exception(e)
    # except ImportError as e:
    #     logger.exception(e)
    # except TSDBError as e:
    #     logger.exception(e)
    except Exception as e:
        logger.error(e)
    

# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=__cli_parse__)

# sets the command infos
COMMAND_INFO = {
    'name': 'profile-to-dmrs-rdf',           # Required
    'help': 'delphin profile to dmrs-rdf',   # Optional
    'description': __doc__,                 # Optional
    'parser': parser,                       # Required
}

# sets the user options
parser.add_argument(
    "profile",
    help="profile path")

_default_prefix = "http://example.com/example"
parser.add_argument(
    "-p",
    # "--prefix",
    dest="prefix",
    help=f"URI prefix (default: {_default_prefix})",
    default=_default_prefix)

_default_output = "output.ttl"
parser.add_argument(
    "-o",
    # "--output",
    dest="output",
    help=f"output file name (default: {_default_output})",
    default=_default_output)

_defaut_format = "turtle"
parser.add_argument(
    "-f",
    # "--format",
    dest="format",
    help=f"output file format (default: {_defaut_format})",
    default=_defaut_format)