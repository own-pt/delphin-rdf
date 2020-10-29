from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace

import delphin  
from delphin import eds

# some useful namespaces
EDS = Namespace("http://www.delph-in.net/schema/eds#")
EDSTYPE = Namespace("http://www.delph-in.net/schema/eds#type#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")

def __nodes_to_rdf__(e, graph, edsi, NODES):
    """
    Creates nodes of variables and nodes specifying their properties.

    e - a delphin eds instance to be parsed into RDF format.
    
    graph - and rdflib graph that is used to store the EDS as RDF
    representation.
    
    edsi - The URI of the EDS instance being parsed.

    NODES - the URI namespace dedicated to nodes.
    """
    for node in e.nodes:
        nodeIRI = NODES[node.id]
        nodePredIRI = NODES[node.id + "#predicate"]
        
        #Instantiate the Node
        graph.add((nodeIRI, RDF.type, EDS.Node))
        graph.add((edsi, EDS.hasNode, nodeIRI))
        
        #typing the predicate
        if delphin.predicate.is_surface(node.predicate):
            graph.add((nodePredIRI, RDF.type, EDS.SurfacePredicate))
        elif delphin.predicate.is_abstract(node.predicate):
            graph.add((nodePredIRI, RDF.type, EDS.AbstractPredicate))
        else: #not surface neither abstract
            print("{} is an invalid predicate".format(node.predicate))
            graph.add((nodePredIRI, RDF.type, EDS.NodePredicate))
            
        #Declaring the node predicate
        graph.add((nodeIRI, EDS.hasNodePredicate, nodePredIRI))
        
        # surface and its parts:
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(node.predicate))
        graph.add((nodePredIRI, EDS.hasLemma, Literal(splittedPredicate[0])))
        if splittedPredicate[1] is not None:
            graph.add((nodePredIRI, EDS.hasPos, EDS[splittedPredicate[1]]))
        if splittedPredicate[2] is not None:
            graph.add((nodePredIRI, EDS.hasSense, Literal(splittedPredicate[2])))
        
        #lnk:
        if node.cfrom is not None:
            graph.add((nodeIRI, EDS.cfrom, Literal(node.cfrom)))
        if node.cto is not None:
            graph.add((nodeIRI, EDS.cto, Literal(node.cto)))
        
        # type of node:
        if node.type is not None:
            graph.add((nodeIRI, EDS.hasNodeType, EDSTYPE[node.type]))
        
        # properties
        for prop in node.properties.items():
            graph.add((nodeIRI, EDS[prop[0].lower()], Literal(prop[1].lower())))
            
        # carg
        if node.carg:
            graph.add((nodeIRI, EDS.carg, Literal(node.carg)))


def __edges_to_rdf__(e, graph, NODES):
    """
    Creates nodes of variables and nodes specifying their properties.

    e - a delphin eds instance to be parsed into RDF format.
    
    graph - and rdflib graph that is used to store the EDS as RDF
    representation.

    NODES - the IRI namespace dedicated to nodes.
    """
    for edge in e.edges:
        graph.add((NODES[edge[0]], EDS[edge[1].lower()], NODES[edge[2]]))
        

        
def eds_to_rdf(e, prefix: str, identifier, iname="edsi#eds", graph=None, out=None, text=None, format="turtle"):
    """
    Parses a pydelphin EDS into RDF representation.

    e - a delphin EDS instance to be parsed into RDF format.
    
    prefix - the IRI to be prefixed to the RDF formated eds.
    
    identifier - an string or a list of strings identifying
    the eds. It should be unique, possibly using a composite
    identifier, given in list.
    For instance one may use it as [textid, eds-id] if the
    same text admits various eds interpretations.

    iname - the eds instance name (the eds as RDF node name)
    to be used. As default, it is "edsi#eds".

    graph - and rdflib graph. If given, uses it to store the
    mrs as RDF representation.

    out - filename to serialize the output into.

    text - the text that is represented in eds as RDF. 

    format - file format to serialize the output into.
    """
    
    # Before running this, use delphin.eds.make_ids_unique(e, m) if possible
    
    # same graph for different EDSs
    if graph is None: graph = Graph()
    if type(identifier) == list:
        identifier = "/".join(identifier)
    
    namespace = prefix + "/" + identifier + "/"

    edsi = URIRef(namespace + iname)
    graph.add((edsi, RDF.type, EDS.EDS))

    NODES = Namespace(namespace + "nodes#")
    __nodes_to_rdf__(e, graph, edsi, NODES)

    #Adding top
    graph.add((edsi, EDS['hasTop'], NODES[e.top]))
    
    __edges_to_rdf__(e, graph, NODES)
    
    # add text as one graph node if it's given
    if text is not None: graph.add((edsi, EDS.text, Literal(text)))
    # serializes graph if given an output file
    if out is not None: graph.serialize(destination=out, format=format)

    return graph
