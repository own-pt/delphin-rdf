"""
Tests if a given profile is parsed.
"""

from delphin import ace
from delphin import itsdb
from delphin import tsql
from delphin import dmrs, eds
from delphin.codecs import eds as edsnative
from delphin.codecs import simplemrs
from delphin.codecs import dmrx

# import parser as p
from delphin.rdf import parser as p
from rdflib import Graph
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="profile path")
ts = itsdb.TestSuite(parser.parse_args().profile)
graph = Graph()
for row in tsql.select('i-id mrs', ts):
    m = simplemrs.decode(row[1])
    p.mrs_to_rdf(m, "http://example.com/example", row[0], graph)

# seralizes the results
graph.serialize(destination="test.ttl", format="turtle")
