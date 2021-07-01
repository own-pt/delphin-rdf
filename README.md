# DELPH-IN formats in RDF

DELPHIN-RDF is a plugin for [pydelphin](https://github.com/delph-in/pydelphin/) for representing textual based semantics as RDF graphs. Here we discuss how DELPH-IN formats can be represented in RDF.  This can be considered a continuation of some discussion started [here](http://moin.delph-in.net/WeSearch/Rdf).

The [pydelphin](https://pypi.org/project/PyDelphin/) and [rdflib](https://pypi.org/project/rdflib/) libraries are required.

## Features

DELPHIN-RDF presents the following dependencies:
- `delphin.rdf`: the main module responsible for mrs/eds/dmrs parsing to RDF.
- `delphin.cli`: pydelphin standard cli path. Here are modules describing the delphin subcommands. See [delphin.cli](https://pydelphin.readthedocs.io/en/latest/api/delphin.cli.html)

Besides that, in `tests` there are use examples. In `doc` there are some references. In `vocabularies` there is the modelling of the semantic representations in RDF.

## Command Line Interface

All the modules in this package can be imported and used as a python module, but DELPHIN-RDF declares `profile-to-rdf` a delphin subcommands of the PyDelphin CLI.

To use the function of the transformation as a python module, it's only needed to import `delphin.rdf`, which exports three main functions: `mrs_to_rdf`, `dmrs_to_rdf` and `eds_to_rdf`. For example, to serialize a profile to DMRS-RDF, we can do
```python
import delphin.rdf as drdf
from delphin import itsdb
from delphin import tsql
from delphin.dmrs import from_mrs as dmrs_from_mrs
from delphin.codecs.simpledmrs import decode
from rdflib import Graph

path_to_profile = "./erg/trunk/tsdb/gold/mrs"
ts = itsdb.TestSuite(path_to_profile)
graph = Graph()
for (parse_id, result_id, text, mrs_string) in tsql.select('parse-id result-id i-input mrs', ts):
  obj = dmrs_from_mrs(decode(mrs_string))
  graph = drdf.dmrs_to_rdf(obj,
                           identifier=[str(parse_id), str(result_id)],
                           graph=graph,
                           text=text)
                          
graph.serialize("./dmrs-erg-gold.nt", format="nt")
```

## Development

One may be able to install delphin-rdf in developer mode, running
```bash
$ pip install -e /path/to/delphin-rdf
```
You're able to remove the package simply by running
```bash
$ pip uninstall delphin-rdf
```
It's advised to install it using a python virtual environment.
