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
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

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
            graph.add((nodePredIRI, RDF.type, DELPH.SurfacePredicate))
        elif delphin.predicate.is_abstract(node.predicate):
            graph.add((nodePredIRI, RDF.type, DELPH.AbstractPredicate))
        else: #not surface neither abstract
            print("{} is an invalid predicate".format(node.predicate))
            graph.add((nodePredIRI, RDF.type, DELPH.Predicate))
            
        #Declaring the node predicate
        graph.add((nodeIRI, DELPH.hasPredicate, nodePredIRI))
        
        # surface and its parts:
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(node.predicate))
        if splittedPredicate[0] is not None: #is this possible?
            graph.add((nodePredIRI, DELPH.hasLemma, Literal(splittedPredicate[0])))
        if splittedPredicate[1] is not None:
            graph.add((nodePredIRI, DELPH.hasPos, POS[splittedPredicate[1]]))
        if splittedPredicate[2] is not None:
            graph.add((nodePredIRI, DELPH.hasSense, Literal(splittedPredicate[2])))
        
        #lnk:
        if node.cfrom is not None: 
            graph.add((nodeIRI, DELPH.cfrom, Literal(node.cfrom)))
        if node.cto is not None:
            graph.add((nodeIRI, DELPH.cto, Literal(node.cto)))
        
        # type of node:
        if node.type is not None:
            graph.add((nodeIRI, RDF.type, DELPH[node.type]))
        
        # properties
        for prop in node.properties.items():
            graph.add((nodeIRI, ERG[prop[0].lower()], Literal(prop[1].lower())))
            
        # carg
        if node.carg:
            graph.add((nodeIRI, DELPH.carg, Literal(node.carg)))


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

    #creating the instance URI and the namespace of nodes
    edsi = URIRef(namespace + iname)
    graph.add((edsi, RDF.type, EDS.EDS))
    NODES = Namespace(namespace + "nodes#")

    #creating the prefixes of the output
    graph.bind("eds", EDS)
    graph.bind("delph", DELPH)
    graph.bind("erg", ERG)
    graph.bind("pos", POS)
    
    #Creating the RDF triples
    __nodes_to_rdf__(e, graph, edsi, NODES)
    #Adding top
    graph.add((edsi, DELPH['hasTop'], NODES[e.top]))
    __edges_to_rdf__(e, graph, NODES)
    
    # add text as one graph node if it's given
    if text is not None: graph.add((edsi, DELPH.text, Literal(text)))
    # serializes graph if given an output file
    if out is not None: graph.serialize(destination=out, format=format)

    return graph
