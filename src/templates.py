# http://example.com/2020/09/sample#1/mrs   -- instancia de MRS
# http://example.com/2020/09/sample#1/h1    -- instancia de handle
# http://example.com/2020/09/sample#1/x12   -- instancia de node

# http://example.com/2020/09/sample?text=1#mrs   -- instancia de MRS
# http://example.com/2020/09/sample?text=1#h1    -- instancia de handle
# http://example.com/2020/09/sample?text=1#x12   -- instancia de node

# http://example.com/2020/09/sample/1#mrs   -- instancia de MRS
# http://example.com/2020/09/sample/1#h1    -- instancia de handle
# http://example.com/2020/09/sample/1#x12   -- instancia de node
# ...

# http://example.com/2020/09/sample/1       -- instancia de MRS
# http://example.com/2020/09/sample/1/h1    -- instancia de handle
# http://example.com/2020/09/sample/1/x12   -- instancia de node
# ...

#
# mrsi1:mrs
# mrsi1:h2
# mrsi1:x12
# ...

class Simplified:
    """
    Defines some usefull templates:
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

    def __init__(self,prefix,identifier):
        """
        Makes a template with prefix and identifier from folowing
        meta-template.

        prefix: general URI prefix wich attemps to describe
        the purposes/fonts/repositories/organizations/etc.
        related to the texts parsing purpose.

        identifier: defines identification for specific text
        from organization defined in the prefix.
        """

        self.node = f"""mrsi{identifier}:{{var}} a mrs:Node ."""
        self.handle = f"""mrsi{identifier}:{{var}} a mrs:Handle ."""

        self.main = f"""
# {{text}}

# prefixes
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix mrs: <http://www.depin-rdf/2020/09/mrs#> .

@prefix  mrsi{identifier}: <{prefix}#{identifier}/> .

# mrs instance declaration
mrsi{identifier}:mrs a mrs:MRS .

# the text instance represented
mrsi{identifier}:mrs mrs:text "{{text}}" .

# individual nodes declaration
{{nodes}}

# individual handles declaration
{{handles}}

# describe RELS trough hasEP
{{rels}}

# describe HCONS trough hasHCONS
{{hcons}}

# describe ICONS
{{icons}}"""

        self.rel = f"""
mrsi{identifier}:mrs rdf:hasEP mrsi{identifier}:EP{{i}} .
mrsi{identifier}:EP{{i}} a mrs:ElementaryPredication .
mrsi{identifier}:EP{{i}} mrs:label mrsi{identifier}:{{label}} .
mrsi{identifier}:EP{{i}} mrs:predicate "{{predicate}}" .
mrsi{identifier}:EP{{i}} mrs:cfrom "{{cfrom}}"^^xsd:integer .
mrsi{identifier}:EP{{i}} mrs:cto "{{cto}}"^^xsd:integer  .
mrsi{identifier}:EP{{i}} mrs:variable mrsi{identifier}:{{variable}} .

{{args}}"""

        self.rel_args_var = f"""mrsi{identifier}:mrs rdf:{{hole}} mrsi{identifier}:{{arg}} ."""
        self.rel_args_int = f"""mrsi{identifier}:mrs rdf:{{hole}} "{{arg}}"^^xsd:integer ."""
        self.rel_args_dec = f"""mrsi{identifier}:mrs rdf:{{hole}} "{{arg}}"^^xsd:decimal ."""
        self.rel_args_boo = f"""mrsi{identifier}:mrs rdf:{{hole}} "{{arg}}"^^xsd:boolean ."""
        self.rel_args_str = f"""mrsi{identifier}:mrs rdf:{{hole}} "{{arg}}"^^xsd:string ."""
        self.rel_args_def = f"""mrsi{identifier}:mrs rdf:{{hole}} "{{arg}}" .""" # literal as default

        self.hcons = f"""
mrsi{identifier}:mrs mrs:hasHCONS mrsi{identifier}:hcons{{i}} .
mrsi{identifier}:hcons{{i}} a mrs:HCONS .
mrsi{identifier}:hcons{{i}} mrs:harg mrsi{identifier}:{{harg}} .
mrsi{identifier}:hcons{{i}} mrs:larg mrsi{identifier}:{{larg}} .
mrsi{identifier}:hcons{{i}} mrs:rel mrs:{{rel}} ."""

        self.icons = f"""
mrsi{identifier}:mrs mrs:hasICONS mrsi{identifier}:icons{{i}} .
mrsi{identifier}:icons{{i}} a mrs:ICONS .
mrsi{identifier}:icons{{i}} mrs:harg mrsi{identifier}:{{harg}} .
mrsi{identifier}:icons{{i}} mrs:larg mrsi{identifier}:{{larg}} .
mrsi{identifier}:icons{{i}} mrs:rel "{{rel}}" ."""