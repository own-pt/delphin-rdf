"""
DELPHIN.RDF

DELPHIN.RDF is a plugin for representing textual based semantics
as RDF graphs. We discuss how DELPH-IN formats can be represented
in RDF.

For more details: https://github.com/arademaker/delph-rdf
"""

from delphin.rdf._dmrs_parser import dmrs_to_rdf
from delphin.rdf._eds_parser import eds_to_rdf
from delphin.rdf._mrs_parser import mrs_to_rdf

# import version
from delphin.rdf.__about__ import __version__

__all__ = [
    'dmrs_to_rdf',
    'eds_to_rdf',
    'mrs_to_rdf',
]