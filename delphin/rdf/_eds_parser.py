from rdflib.graph import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace
from rdflib import plugin
from rdflib.store import Store
from rdflib.term import BNode
import rdflib

import delphin.eds
import delphin.variable
import delphin.predicate

# some useful namespaces
EDS = Namespace("http://www.delph-in.net/schema/eds#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

def eds_to_rdf(e:delphin.eds._eds.EDS, 
               EDSI: rdflib.term.URIRef, 
               store:rdflib.plugins.memory.IOMemory=plugin.get("IOMemory", Store)(),
               defaultGraph:rdflib.graph.Graph=None) -> rdflib.plugins.memory.IOMemory: 
    """
    Takes a PyDelphin EDS object "e" and serializes it into a named RDF graph inside a store.
    
    Args:
        e: a PyDelphin EDS instance to be converted into RDF format
        EDSI: URI of the EDS instance being converted
        store: RDFLib IOMemory store to add the graphs. 
        defaultGraph : the default graph of the store. If not given, creates one from the 'store'.
    Inplace function that alters the store with the serialized EDS and return the store as well.
    """
    # Before running this, use delphin.eds.make_ids_unique(e, m) if possible

   # Making the arguments behave well:
    if defaultGraph is None:
        defaultGraph = Graph(store, identifier=BNode())

    if defaultGraph.store != store: # Bad function input
        defaultGraph = Graph(store, identifier=BNode())
        print("'defaultGraph' argument not consistent with the 'store' argument. The argument was discarded")

    # EDS graph:
    edsGraph = Graph(store, identifier=EDSI)

    # Creating the prefix of the EDSI elements and relevant namespaces
    insprefix = Namespace(EDSI + '#')
    NODES = Namespace(insprefix + "node-")
    PREDS = Namespace(insprefix + "predicate-")
    SORTINFO = Namespace(insprefix + "sortinfo-")

    # Adding top
    edsGraph.add((EDSI, DELPH['hasTop'], NODES[e.top]))

    # creating the prefixes of the output
    # graph.bind("eds", EDS)
    # graph.bind("delph", DELPH)
    # graph.bind("erg", ERG)
    # graph.bind("pos", POS)
    
    # Populating the graphs
    __nodes_to_rdf__(e, edsGraph, defaultGraph, EDSI, NODES, PREDS, SORTINFO)
    __edges_to_rdf__(e, edsGraph, NODES)

    return store


def __nodes_to_rdf__(e, edsGraph, defaultGraph, EDSI, NODES, PREDS, SORTINFO):
    """
    Creates in the graphs the nodes of EDS predications and their properties.

    Args:
        e: a PyDelphin EDS instance to be converted into RDF format
        edsGraph: rdflib Graph of a Store of graphs where the EDS triples will be put.
        defaultGraph: the default graph of the Store with the edsGraph
        EDSI: the node of the EDS instance being converted
        NODES: the URI namespace dedicated to EDS predications
        PREDS: the URI namespace dedicated to predicates
        SORTINFO: the URI namespace dedicated to the sortinfo (morphosemantic information).
    """
    for node in e.nodes:
        nodeURI = NODES[node.id]
        predURI = PREDS[node.id]
        sortinfoURI = SORTINFO[node.id]
        
        edsGraph.add((nodeURI, RDF.type, EDS.Node))
        edsGraph.add((sortinfoURI, RDF.type, DELPH.SortInfo))

        # Information about the EDS node
        edsGraph.add((EDSI, EDS.hasNode, nodeURI))
        edsGraph.add((nodeURI, DELPH.hasPredicate, predURI))
        edsGraph.add((nodeURI, DELPH.hasSortInfo, sortinfoURI))
        edsGraph.add((nodeURI, EDS.nodeIdentifier, Literal(node.id))) # review later if this is useful
        edsGraph.add((nodeURI, RDFS.label, Literal(f"{delphin.predicate.normalize(node.predicate)}<{node.cfrom},{node.cto}>")))
        #type:
        if node.type is not None:
            edsGraph.add((nodeURI, RDF.type, DELPH[node.type]))
        
        # Information about the predicate
        edsGraph.add((predURI, DELPH.predText, Literal(delphin.predicate.normalize(node.predicate))))
        if delphin.predicate.is_surface(node.predicate):
            edsGraph.add((predURI, RDF.type, DELPH.SurfacePredicate))
        elif delphin.predicate.is_abstract(node.predicate):
            edsGraph.add((predURI, RDF.type, DELPH.AbstractPredicate))
        else: #not surface neither abstract
            edsGraph.add((predURI, RDF.type, DELPH.Predicate))
            print(f"{node.predicate} is an invalid predicate.")
        
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(node.predicate))
        if splittedPredicate[0] is not None: #is this possible?
            edsGraph.add((predURI, DELPH.hasLemma, Literal(splittedPredicate[0])))
        if splittedPredicate[1] is not None:
            edsGraph.add((predURI, DELPH.hasPos, POS[splittedPredicate[1]]))
        if splittedPredicate[2] is not None:
            edsGraph.add((predURI, DELPH.hasSense, Literal(splittedPredicate[2])))
        
        #lnk:
        if node.cfrom is not None: 
            edsGraph.add((nodeURI, DELPH.cfrom, Literal(node.cfrom)))
        if node.cto is not None:
            edsGraph.add((nodeURI, DELPH.cto, Literal(node.cto)))
        
        # properties
        for prop in node.properties.items():
            edsGraph.add((sortinfoURI, ERG[prop[0].lower()], Literal(prop[1].lower())))
        
        # carg; review later
        if node.carg:
            edsGraph.add((nodeURI, DELPH.carg, Literal(node.carg)))


def __edges_to_rdf__(e, edsGraph, NODES):
    """
    Creates in the graph triples that links the EDS nodes, the edges.

    Args:
        e: a PyDelphin EDS instance to be converted into RDF format
        edsGraph: rdflib Graph of a Store of graphs where the EDS triples will be put.
        NODES: the URI namespace dedicated to EDS predications
    """
    for edge in e.edges:
        edsGraph.add((NODES[edge[0]], EDS[edge[1].lower()], NODES[edge[2]]))
        

        
