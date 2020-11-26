"""
WeSearch Query Language (WQL) into Sparql for RDF queries.

: (colon), separates optional node identifier from node content;
[ (left square bracket), separates node properties from outgoing arcs;
] (right square bracket), terminates a list of outgoing arcs;
  (whitespace), separates role labels and values in list of arcs;
, (comma), separates role–value pairs within list of outgoing arcs;
+ (plus sign), indicates (optional) lemma object property;
/ (slash), indicates (optional) pos property;
? (question mark), Lucene-style single-character wildcard;
* (asterisk), Lucene-style arbitrary sub-string wildcard;
| (vertical bar), logical disjunction (see below);
( and ) (left and right parentheses), grouping of sub-expressions (see below);
! (exclamation mark), reserved for negation (to be defined);
\ (backslash), escape character, suppressing operator status for all of the above.

see: http://moin.delph-in.net/WeSearch/QueryLanguage
"""

import argparse
import logging
logger = logging.getLogger("wql")

from _to_tree import _parse
from _to_tree import _push_nots
from _to_tree import tree_to_str

from _to_sparql import _to_sparql_structure

def generate_sparql(query:str):
    """
    Parses a WQL query into SPARQL language using a MRS
    based output format at first.
    
    Args:
        query : a WQL formated query to be parsed
    
    Output:
        a string containing MRS  SPARQL query
    """

    # format query and evaluate query tree
    logger.info(f"parsing query: {query}")
    query = _parse(query)
    logger.debug(f"parsed query tree: \n{tree_to_str(query)}")
    query = _push_nots(query)
    logger.debug(f"optmized query tree: \n{tree_to_str(query)}")


    # parse to sparql structure than string
    logger.info(f"parsing query tree into sparql...")
    sparql = _to_sparql_structure(query)

    print(sparql)



# ProcessingDefaults
# - sparql = exp.generateSparql(query)
#   - query = query.parse(query)
#     - separamos e parseamos o QEQ
#     - separamos e parseamos o corpo
#       - query = format(query) : espaços, ajustamos operacoes, consideramos caracteres e localizacao
#       - query = recognize(query) : extruturamos arvore, (compacto: processado?), nós (nao operados), operacoes, roles, IDs, validacao
#         - searchOperator()
#         - parseNodes()
#       - pushNot(query) : demorgan simplificando a expressao
#  - sparql = toSparqlStructure(query)
#    - initialize(output) : prefixos
#    - toSparql(parsed, aux) : recusivo; operacao ou folha
#      - toSparqlOperator()
#      - toSparqlNode()
#    - adicionamos sufixos, ordenacao, variaveis, etc

# define Command Line Interface arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    dest="sentence",
    help="expression to be parsed",
    default="[* x]{h1 =q h3, h1 =q h2}")
parser.add_argument(
    '-v', '--verbose',
    action='count',
    dest='verbosity',
    default=0)

args = parser.parse_args()

# define Command Line Interface verbosity
base_loglevel = 30
verbosity = min(args.verbosity, 2)
loglevel = base_loglevel - (args.verbosity * 10)
logging.basicConfig(level=loglevel)

generate_sparql(args.sentence)