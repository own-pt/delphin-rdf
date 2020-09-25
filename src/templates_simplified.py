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

# the text instance represented
mrsi:mrs mrs:text "{text}" .

# individual nodes declaration
{nodes}

# individual handles declaration
{handles}

# describe RELS trough hasEP
{rels}

# describe HCONS trough hasHCONS
{hcons}

# describe ICONS
{icons}"""

rel = """
mrsi:mrs rdf:hasEP mrsi:EP{i} .
mrsi:EP{i} a mrs:ElementaryPredication .
mrsi:EP{i} mrs:label mrsi:{label} .
mrsi:EP{i} mrs:predicate "{predicate}" .
mrsi:EP{i} mrs:variable mrsi:{variable} .

{args}"""

rel_args_var = """mrsi:mrs rdf:{hole} mrsi:{arg} ."""
rel_args_int = """mrsi:mrs rdf:{hole} "{arg}"^^xsd:integer ."""
rel_args_dec = """mrsi:mrs rdf:{hole} "{arg}"^^xsd:decimal ."""
rel_args_boo = """mrsi:mrs rdf:{hole} "{arg}"^^xsd:boolean ."""
rel_args_str = """mrsi:mrs rdf:{hole} "{arg}"^^xsd:string ."""
rel_args_def = """mrsi:mrs rdf:{hole} "{arg}" .""" # literal as default

hcons = """
mrsi:mrs mrs:hasHCONS mrs:hcons{i} .
mrsi:hcons{i} a mrs:HCONS .
mrsi:hcons{i} mrs:harg mrsi:{harg} .
mrsi:hcons{i} mrs:larg mrsi:{larg} .
mrsi:hcons{i} mrs:rel mrs:{rel} ."""

icons = """
mrsi:mrs mrs:hasICONS mrs:Icons{i} .
mrsi:icons{i} a mrs:ICONS .
mrsi:icons{i} mrs:harg mrsi:{harg} .
mrsi:icons{i} mrs:larg mrsi:{larg} .
mrsi:icons{i} mrs:rel "{rel}" ."""