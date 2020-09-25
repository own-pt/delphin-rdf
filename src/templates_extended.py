"""
We define some usefull templates:
  main: defines main structure, wich receives all
  a sort of defiintions such as Nodes, Handles, etc.
  
  rels: describes relations, wich receives label,
  node, predicate, and other arguments.

  rels_args: describes other arguments in rels.

  hcons: describes the hcons, receiving arguments
  and a reasonable relation among qeq, lheq, or outscopes.

  icons: describes the icons, receiving arguments
  and a reasonable predicate defined by a grammar.
"""

node = """mrsi:{var} a mrs:Node ."""

handle = """mrsi:{var} a mrs:Handle ."""

main = """
# {text}

# prefixes
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix mrs: <http://depin-rdf/2020/mrs#> .
@prefix mrsi: <http://depin-rdf/2020/mrs-instance#> .

# mrs instance declaration
mrsi:mrs a mrs:MRS .

# individual nodes declaration
{nodes}

# individual handles declaration
{handles}

# describe RELS
mrsi:rels a mrs:RELS .
mrsi:mrs mrs:hasRELS mrsi:rels .
{rels}

# describe HCONS
mrsi:hcons a mrs:HCONS .
mrsi:mrs mrs:hasHCONS mrsi:hcons .
{hcons}

# describe ICONS
mrsi:icons a mrs:ICONS .
mrsi:mrs mrs:hasICONS mrsi:icons .
{icons}"""

rel = """
mrsi:rels rdf:_{i} _:rel{i} .
_:rel{i} a mrs:ElementaryPredication .
_:rel{i} mrs:predicate "{predicate}" .
_:rel{i} mrs:label mrsi:{label} .
_:rel{i} mrs:variable mrsi:{variable} .
_:rel{i} mrs:arguments _:args{i} .

_:args{i} a rdf:Bag .
{args}"""

rel_args_var = """_:args{i} rdf:_{j} mrsi:{arg} ."""
rel_args_int = """_:args{i} rdf:_{j} "{arg}"^^xsd:integer ."""
rel_args_dec = """_:args{i} rdf:_{j} "{arg}"^^xsd:decimal ."""
rel_args_boo = """_:args{i} rdf:_{j} "{arg}"^^xsd:boolean ."""
rel_args_str = """_:args{i} rdf:_{j} "{arg}"^^xsd:string ."""
rel_args_def = """_:args{i} rdf:_{j} "{arg}" .""" # literal as default

hcons = """
mrsi:hcons rdf:_{i} _:hcons{i} .
_:hcons{i} a mrs:Constraint .
_:hcons{i} mrs:harg mrsi:{harg} .
_:hcons{i} mrs:larg mrsi:{larg} .
_:hcons{i} mrs:rel "{rel}" ."""

icons = """
mrsi:icons rdf:_{i} _:icons{i} .
_:icons{i} a mrs:Constraint .
_:icons{i} mrs:harg mrsi:{harg} .
_:icons{i} mrs:larg mrsi:{larg} .
_:icons{i} mrs:rel "{rel}" ."""