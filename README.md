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

## Development

One may be able to install delphin-rdf in developer mode, running
```bash
$ pip install -e /path/to/delphin-rdf
```
Wich allows you to remove the package simply by running
```bash
$ pip uninstall delphin-rdf
```
It's advised to install it using a python virtual environment.
