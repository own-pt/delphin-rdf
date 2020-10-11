from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace

import delphin
from delphin import mrs

# some usefull namespaces
MRS = Namespace("http://www.delph-in.net/schema/mrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")

def vars_to_rdf(m, variables, graph, VARS):
    """"""

    for v in variables.keys():
        # handle variables
        if delphin.variable.type(v) == "h":
            # here we should add the some more information
            graph.add((VARS[v], RDF.type, MRS.Handle))
        
        # node variables
        else:
            # here we should add the some more information
            graph.add((VARS[v], RDF.type, MRS.Node))
        
def rels_to_rdf(m, rels, graph, mrsi, RELS, VARS):
    """"""
    
    for rel in range(len(rels)):
        mrs_rel = rels[rel]
        rdf_rel = RELS["EP{rel}".format(rel=rel)]

        graph.add((mrsi, MRS.hasEP, rdf_rel))
        graph.add((rdf_rel, RDF.type, MRS.ElementaryPredication))
        
        graph.add((rdf_rel, MRS.label, VARS[mrs_rel.label]))
        graph.add((rdf_rel, MRS.var, VARS[mrs_rel.iv]))
        graph.add((rdf_rel, MRS.predicate, Literal(mrs_rel.predicate)))
        graph.add((rdf_rel, MRS.cto, Literal(mrs_rel.cto)))     # integer
        graph.add((rdf_rel, MRS.cfrom, Literal(mrs_rel.cfrom))) # integer

        # parse arguments
        
        for hole, arg in mrs_rel.args.items():
            #if hole == "ARG0": continue
            # arg_type = type(eval(arg.title()))

            # mrs variables as arguments
            if arg in m.variables:
                graph.add((rdf_rel, MRS[hole], VARS[arg]))
            # any other kind of arguments
            else:
                graph.add((rdf_rel, MRS[hole], Literal(arg)))
    

def hcons_to_rdf(m, hcons, graph, mrsi, HCONS, VARS):
    """"""
    
    for hcon in range(len(hcons)):
        mrs_hcon = hcons[hcon]
        rdf_hcon = HCONS["hcon{hcon}".format(hcon=hcon)]
        
        # adds hcon to graph
        graph.add((mrsi, MRS.hasHCONS, rdf_hcon))
        graph.add((rdf_hcon, RDF.type, MRS.HCONS))
        graph.add((rdf_hcon, MRS.harg, VARS[mrs_hcon.hi]))
        graph.add((rdf_hcon, MRS.larg, VARS[mrs_hcon.lo]))

        # this relation sould be defined in MRS
        graph.add((rdf_hcon, MRS.rel, MRS[mrs_hcon.relation]))

def icons_to_rdf(m, icons, graph, mrsi, ICONS, VARS):
    """"""
    
    for icon in range(len(icons)):
        mrs_icon = icons[icon]
        rdf_icon = ICONS["icon{icon}".format(icon=icon)]
        
        # adds hcon to graph
        graph.add((mrsi, MRS.hasICONS, rdf_icon))
        graph.add((rdf_icon, RDF.type, MRS.HCONS))
<<<<<<< HEAD
        graph.add((rdf_icon, MRS.harg, VARS[mrs_icon.hi])) # should be revisited
        graph.add((rdf_icon, MRS.larg, VARS[mrs_icon.lo])) # should be revisited
=======
        graph.add((rdf_icon, MRS.harg, VARS[mrs_icon.left])) # should be revisited
        graph.add((rdf_icon, MRS.larg, VARS[mrs_icon.right])) # should be revisited
>>>>>>> rademaker/master

        # this relation sould be defined by grammar
        graph.add((rdf_icon, MRS.rel, Literal(mrs_icon.relation)))


def mrs_to_rdf(m, prefix, identifier, graph=None, out=None, text=None, format="turtle"):
    """
    m: a pyldelphin mrs instance to be parsed into rdf.
    prefix: the URI prefixed to RDF representation
    identifier: an identifier for the parsed text
    """

    # it's possible to use the same graph for
    # different mrs representations if usefull
    if graph == None: graph = Graph()
    
    namespace = prefix + "/" + identifier + "/"

    mrsi = URIRef(namespace + "mrsi#mrs0")
<<<<<<< HEAD
    graph.add((mrsi, RDF.type, mrs.MRS))
=======
    graph.add((mrsi, RDF.type, MRS.MRS))
>>>>>>> rademaker/master

    VARS = Namespace(namespace + "variables#")
    RELS = Namespace(namespace + "rels#")
    HCONS = Namespace(namespace + "hcons#")
    ICONS = Namespace(namespace + "icons#")

    vars_to_rdf(m, m.variables, graph, VARS)
    rels_to_rdf(m, m.rels, graph, mrsi, RELS, VARS)
    hcons_to_rdf(m, m.hcons, graph, mrsi, HCONS, VARS)
    icons_to_rdf(m, m.icons, graph, mrsi, ICONS, VARS)

    # add text as one graph node if it's given
    if text: graph.add((mrsi, MRS.text, Literal(text)))
    # serializes graph if given an output file
    if out: graph.serialize(destination=out,format=format)

    return graph
