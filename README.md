# DELPH-IN formats in RDF

DELPHIN-RDF is a plugin for [pydelphin](https://github.com/delph-in/pydelphin/) for representing textual based semantics as RDF graphs. Here we discuss how DELPH-IN formats can be represented in RDF.  This can be considered a continuation of some discussion started [here](http://moin.delph-in.net/WeSearch/Rdf).

The [pydelphin](https://pypi.org/project/PyDelphin/) and [rdflib](https://pypi.org/project/rdflib/) libraries are required.

## Features

DELPHIN-RDF presents the following dependencies:
- `delphin.rdf`: the main module responsible for mrs/eds/dmrs parsing to RDF.
- `delphin.cli`: pydelphin standard cli path. Here are modules describing the delphin subcommand. See [delphin.cli](https://pydelphin.readthedocs.io/en/latest/api/delphin.cli.html)

Besides that, in `tests` there are use examples. In `doc` there are some references. In `vocabularies` there is the modelling of the semantic representations in RDF.

## Command Line Interface

All the modules in this package can be imported and used as a Python module, but DELPHIN-RDF declares `profile-to-rdf`, a delphin subcommand of the PyDelphin CLI.
This subcommand requires the path to the profile to serialize as argument. There are optional arguments, such as the format of the output (`-f`), the representation to serialize (`--to`), the prefix of the URIs in the RDF (`-p`) and the name of the output file (`-o`).

## Python module

To use the function of the transformation as a Python module, it's only needed to import `delphin.rdf`, which exports three main functions: `mrs_to_rdf`, `dmrs_to_rdf` and `eds_to_rdf`. They operate on a [ConjunctiveGraph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.ConjunctiveGraph) RDFLib object, creating named graphs for each instance in the context of this conjunctive graph, which is the graph that has all quads of a specific store. For example, to serialize a profile to DMRS-RDF, we can do
```python
import delphin.rdf as drdf
from delphin import itsdb, tsql
from delphin.dmrs import from_mrs as dmrs_from_mrs
from delphin.codecs.simpledmrs import decode
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import URIRef, Namespace, Literal RDF, RDFS

path_to_profile = "./erg/trunk/tsdb/gold/mrs"
ts = itsdb.TestSuite(path_to_profile)
defaultGraph = ConjunctiveGraph()
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")
DMRS = Namespace("http://www.delph-in.net/schema/dmrs#")
defaultGraph.bind("erg", ERG)
defaultGraph.bind("delph", DELPH)
defaultGraph.bind("pos", POS)
defaultGraph.bind("dmrs", DMRS)
prefix = "http://example.com"
PROFILE = URIRef(prefix)
defaultGraph.add((PROFILE, RDF.type, DELPH.Profile))

for (parse_id, result_id, text, mrs_string) in tsql.select('parse-id result-id i-input mrs', ts):
  obj = dmrs_from_mrs(decode(mrs_string))
  ITEM = URIRef(f"{prefix}/{parse_id}")
  RESULT = URIRef(f"{prefix}/{parse_id}/{result_id}")
  DMRSI = URIRef(f"{prefix}/{parse_id}/{result_id}/dmrs")
        
  defaultGraph.add((ITEM, RDF.type, DELPH.Item))
  defaultGraph.add((RESULT, RDF.type, DELPH.Result))
  defaultGraph.add((MRSI, RDF.type, DMRS.DMRS))
        
  defaultGraph.add((ITEM, DELPH.hasText, Literal(text)))
        
  defaultGraph.add((PROFILE, DELPH.hasItem, ITEM))
  defaultGraph.add((ITEM, DELPH.hasResult, RESULT))
  defaultGraph.add((RESULT, DELPH.hasDMRS, DMRSI))

  drdf.dmrs_to_rdf(dmrs_from_mrs(simplemrs.decode(mrs_string)), 
                   DMRSI, 
                   defaultGraph) #inplace, change defaultGraph
                          
defaultGraph.serialize("./dmrs-erg-gold.nq", format="nquads")
```

## Development

One may be able to install delphin-rdf in developer mode cloning this repo and running
```bash
$ pip install -e /path/to/delphin-rdf
```
You're able to remove the package simply by running
```bash
$ pip uninstall delphin-rdf
```
It's advised to install it using a python virtual environment.
