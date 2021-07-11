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

To use the function of the transformation as a Python module, it's only needed to import `delphin.rdf`, which exports three main functions: `mrs_to_rdf`, `dmrs_to_rdf` and `eds_to_rdf`. They operate on [IO Memory](https://rdflib.readthedocs.io/en/stable/_modules/rdflib/plugins/memory.html#IOMemory) RDFLib object, creating named graphs for each instance in the context of this optimizd RDFLib store. For example, to serialize a profile to DMRS-RDF, we can do
```python
import delphin.rdf as drdf
from delphin import itsdb
from delphin import tsql
from delphin.dmrs import from_mrs as dmrs_from_mrs
from delphin.codecs.simpledmrs import decode
from rdflib import plugin
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.store import Store
from rdflib.term import BNode
from rdflib import URIRef
from rdflib.store import Store
from rdflib import RDF, RDFS
from rdflib import Namespace, Literal

path_to_profile = "./erg/trunk/tsdb/gold/mrs"
ts = itsdb.TestSuite(path_to_profile)
store = plugin.get("IOMemory", Store)()
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")
DMRS = Namespace("http://www.delph-in.net/schema/dmrs#")
store.bind("erg", ERG)
store.bind("delph", DELPH)
store.bind("pos", POS)
store.bind("dmrs", DMRS)
prefix = "http://example.com"
PROFILE = URIRef(prefix)
defaultGraph = Graph(store, identifier=BNode())
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
                   store, 
                   defaultGraph) #inplace, change store and defaultGraph
                          
ConjunctiveGraph(store).serialize("./dmrs-erg-gold.nq", format="nquads")
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
