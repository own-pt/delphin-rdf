from delphin import itsdb
from delphin import tsql
from delphin.codecs import simplemrs
from delphin.codecs import rdf

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="a profile path")
parser.add_argument("output", help="the output file")
args = parser.parse_args()

output = args.output
ts = itsdb.TestSuite(args.profile)

data = tsql.select('i-id mrs i-input', ts)
ids = ["mrs-id-"+row[0] for row in data]
ms = [simplemrs.decode(row[1]) for row in data]
txs = [row[2] for row in data]

# tests dump
print("##############################################################################")
print(f"Using rdf.dump with output: {output}")
rdf.dump(ms, output, "http://example.com/example", identifiers=ids, texts=txs)

# tests dumps
print("##############################################################################")
print("Using rdf.dumps")
print(rdf.dumps(ms, "http://example.com/example", identifiers=ids, texts=txs))

# tests encode
print("##############################################################################")
print("Using rdf.encode")
print(rdf.encode(ms[0], "http://example.com/example", identifier=ids[0], text=txs[0]))