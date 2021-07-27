"""
Transcribes a profile into a RDF graph.
It creates named graphs, but it has support to creating files only with triples like ntriples or turtle.

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

from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.term import _is_valid_uri
from rdflib import Namespace
from rdflib import plugin
from rdflib.term import BNode
from rdflib import URIRef
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS 

ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

# interface function
def __cli_parse__(args):
    # remove the not well formed sentences? add option?
    # print MRS or parse to DMRS format?

    path = args.profile
    prefix = args.prefix.strip("/")
    semrep = args.semrep.lower()
    parser = None
    # Setting verbosity; need to figure a better solution.
    if args.verbosity == 1:
        logger.setLevel(20)
    elif args.verbosity >= 2:
        logger.setLevel(10)

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
        # validate format and get converter
        to_rdf, from_mrs = _get_converters(semrep)
        
        # open Test Suite and start conversion
        ts = itsdb.TestSuite(path)
        # logger.info(f"Converting {len(ts['result'])} analysis of {len(ts['item'])} sentences from {args.profile}")
        logger.info(f"Converting {len(ts['result'])} analysis of {len(ts['item'])} sentences from {args.profile}")


        # Creating the Conjunctive Graph
        defaultGraph = ConjunctiveGraph()
        PROFILE = URIRef(f"{prefix}") # review later
        defaultGraph.add((PROFILE, RDF.type, DELPH.Profile))
        semrepURI, prof_semrep_relation = _get_RDF_semrep(semrep, defaultGraph)
        defaultGraph.bind("erg", ERG)
        defaultGraph.bind("delph", DELPH)
        defaultGraph.bind("pos", POS)
        # defaultGraph.bind("upref", prefix) # may be useful

        # The tsql takes some time to be processed:
        # logger.info(f"Loading the profile")
        logger.info(f"Loading the profile")
        profile_data = tsql.select('parse-id result-id i-input mrs', ts)
        logger.info(f"Converting the profile")
        # Iterating over the results:
        for (parse_id, result_id, text, mrs_string) in profile_data:
            logger.debug(f"Converting the result {result_id} of sentence {parse_id}")
            m = simplemrs.decode(mrs_string)

            # making sure of the well formedness of "m"
            if not is_well_formed(m):
                logger.warning(f"Result {result_id} of sentence {parse_id} is not well formed")
                # continue

            # converting the MRS object to the representation intended to be converted
            obj = from_mrs(m)
            # logger.debug(f"Result {result_id} of item {parse_id}: \n\t{text}\n\t{obj}\n\t{mrs_string}")
            
            # Creating URIs for relevant resources.
            ITEM = URIRef(f"{prefix}/{parse_id}") # The item part may be redundant, maybe iterate before the itens
            RESULT = URIRef(f"{prefix}/{parse_id}/{result_id}")
            SEMREPI = URIRef(f"{prefix}/{parse_id}/{result_id}/{semrep}")
        
            # adding types:
            defaultGraph.add((ITEM, RDF.type, DELPH.Item))
            defaultGraph.add((RESULT, RDF.type, DELPH.Result))
            defaultGraph.add((SEMREPI, RDF.type, semrepURI))
        
            # Associating text to item:
            defaultGraph.add((ITEM, DELPH.hasText, Literal(text)))
        
            # Linking those nodes:
            defaultGraph.add((PROFILE, DELPH.hasItem, ITEM))
            defaultGraph.add((ITEM, DELPH.hasResult, RESULT))
            defaultGraph.add((RESULT, prof_semrep_relation, SEMREPI))

            to_rdf(
                obj, 
                SEMREPI,
                defaultGraph)

        # serializes results
        logger.info(f"Serializing results to {args.output}")
        defaultGraph.serialize(destination=args.output, format=args.format)
        logger.info(f"DONE")

    # except PyDelphinSyntaxError as e:
    #     logger.exception(e)
    # except ImportError as e:
    #     logger.exception(e)
    # except TSDBError as e:
    #     logger.exception(e)
    except Exception as e:
        logger.error(e)
    
def _get_converters(semrep):
    """
    This function gives us the conversor from MRS to a specific 'semrep'.
    It returns a conversor function of delphin.rdf from this 'semrep' to RDF and
    a function that converts PyDelphin MRS object to the specific semantic representation.
    """
    logger.info(f"Getting parsers for representation: {semrep}")
    if semrep == "mrs":
        logger.info("No conversion necessary")
        return mrs_to_rdf, lambda x: x
    elif semrep == "eds":
        return eds_to_rdf, eds_from_mrs
    elif semrep == "dmrs":
        return dmrs_to_rdf, dmrs_from_mrs
    
    raise PyDelphinException(f"Not a valid format: {semrep}")

def _get_RDF_semrep(semrep, defaultGraph):
    """
    This function binds the prefix of the semantic representation to the conjunctive graph and returns 
    RDFLib objects that are relevant for the conversion
    """
    if semrep == "mrs":
        MRS = Namespace("http://www.delph-in.net/schema/mrs#")
        defaultGraph.bind("mrs", MRS)
        return MRS.MRS, DELPH.hasMRS
    elif semrep == "eds":
        EDS = Namespace("http://www.delph-in.net/schema/eds#")
        defaultGraph.bind("eds",EDS)
        return EDS.EDS, DELPH.hasEDS
    elif semrep == "dmrs":
        DMRS = Namespace("http://www.delph-in.net/schema/dmrs#")
        defaultGraph.bind("dmrs", DMRS)
        return DMRS.DMRS, DELPH.hasDMRS

# sets parser and interface function
parser = argparse.ArgumentParser(add_help=False)
parser.set_defaults(func=__cli_parse__)

# sets the command infos
COMMAND_INFO = {
    'name': 'profile-to-rdf',               # Required
    'help': 'incr tsdb test suite to rdf',  # Optional
    'description': __doc__,                 # Optional
    'parser': parser,                       # Required
}

# sets the user options
parser.add_argument(
    "profile",
    help="profile path")

_default_prefix = "http://example.com/"
parser.add_argument(
    "-p",
    # "--prefix",
    dest="prefix",
    help=f"URI prefix (default: {_default_prefix})",
    default=_default_prefix)

_default_output = "output.nq"
parser.add_argument(
    "-o",
    # "--output",
    dest="output",
    help=f"output file name (default: {_default_output})",
    default=_default_output)

_defaut_format = "nquads"
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
    help=f"(mrs|dmrs|eds) semantic representation to serialize (default: {_default_delphin})",
    default=_default_delphin)
