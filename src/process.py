from delphin import ace
from delphin import itsdb
from delphin import tsql
from delphin import dmrs, eds
from delphin.codecs import eds as edsnative
from delphin.codecs import simplemrs
from delphin.codecs import dmrx

import parser as p
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace


ts = itsdb.TestSuite('~/hpsg/terg/tsdb/gold/mrs')
graph = Graph()
for row in tsql.select('i-id mrs', ts):
    m = simplemrs.decode(row[1])
    p.mrs_to_rdf(m, "http://example.com", row[0], graph)

graph.serialize(destination="teste.ttl",format="turtle")


"""
http://example.com/{item}/{mrsid}/HCONS/{relid}
http://example.com/{item}/{mrsid}/ICONS/{relid}
http://example.com/{item}/{mrsid}/RELS/{relid}
http://example.com/{item}/{mrsid}/VARIABLES/{varid}
"""
