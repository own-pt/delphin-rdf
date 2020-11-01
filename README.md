# DELPH-IN formats in RDF

DELPHIN-RDF's is a plugin for [pydelphin](https://github.com/delph-in/pydelphin/) for representing textual based semantics as RDF graphs. Here we discuss how DELPH-IN formats can be represented in RDF.  This can be consider a continuation of some discussion started [here](http://moin.delph-in.net/WeSearch/Rdf).

The [pydelphin](https://pypi.org/project/PyDelphin/) and [rdflib](https://pypi.org/project/rdflib/) libraries are required.

## Features

DELPHIN-RDF presents the following dependencies:
- `delphin.rdf`: the main package, where we add modules responsible for mrs/eds/dmrs parsing to RDF.
- `delphin.cli`: pydelphin standard cli path. Here are modules describing the delphin subcommands. For now, those are `profile-to-rdf` and `to-rdf`. See [delphin.cli](https://pydelphin.readthedocs.io/en/latest/api/delphin.cli.html)
- `delphin.codecs`: pydelphin standard codecs path. Here are modules responsible for describing pydelphin objects serialization. Those modules are recognized by the library, and may be used as arguments for `delphin convert` subcommand. See [delphin.codecs](https://pydelphin.readthedocs.io/en/latest/api/delphin.codecs.html)

Besides that, there is a `tests` directory, where we add examples and use cases. In `doc` there are some references  and in `vocabularies` there is the modelling of the semantic representations in RDF.

## Command Line Interface

All the modules in this package can be imported and used as a python module, but DELPHIN-RDF describes the following delphin subcommands/options:

- `$ delphin profile-to-rdf`: converts the MRS of a profile to RDF ;
- `$ delphin profile-to-eds-to-rdf`: converts the MRS of a profile to EDS and this one to RDF ;
- `$ delphin profile-to-dmrs-to-rdf`: converts the MRS of a profile to DMRS and this one to RDF ;
- `$ delphin text-to-rdf (not complete/in discussion)`: should convert all possible MRS interpretations of text(s) into RDF graph(s);
- `$ delphin to-rdf (not complete/in discussion)`: should be a general purpose parser, receiving as input a path to a profile/simplemrs/texts, or a *stdin* of simplemrs/texts to be converted into a RDF graph. In case of texts, it should parse all possible MRS interpretations;
- `$ delphin convert --to rdf (not complete)`: better solution than `to-rdf` subcommand; using a codec allows using `delphin convert` environment, to parse different input formats to RDF.

## Development

One may be able to install delphin-rdf in developer mode, running
```bash
$ python /path/to/delphin-rdf/setup.py develop
```
Or, best option, using `pip`
```bash
$ pip install -e /path/to/delphin-rdf
```
The second option allows you to remove the package simply by running
```bash
$ pip uninstall delphin-rdf
```
It's advised to install it using a python virtual environment.
