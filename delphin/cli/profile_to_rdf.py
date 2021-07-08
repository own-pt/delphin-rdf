"""
Transcribes a profile intro a RDF graph.

For more details, see: {https://github.com/own-pt/delphin-rdf}.
"""

from os.path import isdir

import argparse
import warnings
import logging
logger = logging.getLogger(__name__)

# from progress.bar import Bar as ProgressBar

from delphin.exceptions import PyDelphinException, PyDelphinWarning
from delphin.tsdb import TSDBError, TSDBWarning

from delphin.rdf import mrs_to_rdf
from delphin.rdf import eds_to_rdf
from delphin.rdf import dmrs_to_rdf

from delphin.mrs import is_well_formed
from delphin.eds import from_mrs as eds_from_mrs
from delphin.dmrs import from_mrs as dmrs_from_mrs

from delphin.codecs import simplemrs
from delphin.tsdb import is_database_directory
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
    semrep = args.semrep.lower()
    parser = None
    
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
        # validate format and get parsers
        to_rdf, from_mrs = _get_parsers(semrep)
        
        # open Test Suite and start conversion
        ts = itsdb.TestSuite(path)
        # logger.info(f"Converting {len(ts['result'])} analysis of {len(ts['item'])} sentences from {args.profile}")
        logger.log(30,f"Converting {len(ts['result'])} analysis of {len(ts['item'])} sentences from {args.profile}")

        # The tsql takes some time to be processed:
        # logger.info(f"Loading the profile")
        logger.log(30,f"Loading the profile")
        profile_data = tsql.select('parse-id result-id i-input mrs', ts)
        logger.log(30,f"Converting the profile")
        for (parse_id, result_id, text, mrs_string) in profile_data:
            logger.info(f"Converting the result {result_id} of sentence {parse_id}")
            m = simplemrs.decode(mrs_string)

            # making sure of the well formedness of "m"
            if not is_well_formed(m):
                logger.warning(f"Result {result_id} of sentence {parse_id} is not well formed")
                # continue

            # converting the MRS object to the representation intended to be converted
            obj = from_mrs(m)
            logger.debug(f"Result {result_id} of item {parse_id}: \n\t{text}\n\t{obj}\n\t{mrs_string}")
            
            graph = to_rdf(
                        obj,
                        prefix=prefix,
                        identifier=[str(parse_id), str(result_id)],
                        graph=graph,
                        text=text)

        # serializes results
        logger.log(30,f"Serializing results to {args.output}")
        graph.serialize(destination=args.output, format=args.format)
        logger.log(30,f"DONE")

    # except PyDelphinSyntaxError as e:
    #     logger.exception(e)
    # except ImportError as e:
    #     logger.exception(e)
    # except TSDBError as e:
    #     logger.exception(e)
    except Exception as e:
        logger.error(e)
    
def _get_parsers(semrep):
    logger.info(f"Getting parsers for representation: {semrep}")

    if semrep == "mrs":
        logger.info("No conversion necessary")
        return mrs_to_rdf, lambda x: x
    if semrep == "eds":
        return eds_to_rdf, eds_from_mrs
    if semrep == "dmrs":
        return dmrs_to_rdf, dmrs_from_mrs
    
    raise PyDelphinException(f"Not a valid format: {semrep}")

# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=__cli_parse__)

# sets the command infos
COMMAND_INFO = {
    'name': 'profile-to-rdf',               # Required
    'help': 'delphin profile to rdf',       # Optional
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

_default_delphin = "mrs"
parser.add_argument(
    # "-t",
    "--to",
    dest="semrep",
    help=f"(mrs|eds|dmrs) modeled semantic representation (default: {_default_delphin})",
    default=_default_delphin)
