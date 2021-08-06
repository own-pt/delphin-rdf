from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace
from rdflib import plugin
from rdflib.store import Store
from rdflib.term import BNode
import rdflib

import delphin.dmrs
import delphin.variable
import delphin.predicate

# some useful namespaces
DMRS = Namespace("http://www.delph-in.net/schema/dmrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

def dmrs_to_rdf(d:delphin.dmrs._dmrs.DMRS, 
                DMRSI: rdflib.term.URIRef, 
                defaultGraph:rdflib.graph.ConjunctiveGraph=None) -> rdflib.graph.ConjunctiveGraph:
    """
    Takes a PyDelphin DMRS object "d" and serializes it into a named RDF graph inside a store.
    
    Args:
        d: a PyDelphin DMRS instance to be converted into RDF format
        DMRSI: URI of the DMRS instance being converted
        defaultGraph : the conjunctive graph representing the profile graph. If not given, creates one.
    Inplace function that alters the store with the serialized DMRS and return the store as well.
    """
    # Making the arguments behave well:
    if defaultGraph is None:
        defaultGraph = ConjunctiveGraph()

    # DMRS graph:
    dmrsGraph = Graph(store=defaultGraph.store, identifier=DMRSI)

    # Creating the prefix of the DMRS elements and relevant namespaces
    NODES = Namespace(DMRSI + "#node-")
    LINKS = Namespace(DMRSI + "#link-")
    PREDS = Namespace(DMRSI + "#predicate-")
    SORTINFO = Namespace(DMRSI + "#sortinfo-")

    defaultGraph.add((DMRSI, RDF.type, DMRS.DMRS))
    
    # Adding top and index
    dmrsGraph.add((DMRSI, DELPH['hasTop'], NODES[f"{d.top}"]))
    dmrsGraph.add((DMRSI, DELPH['hasIndex'], NODES[f"{d.index}"]))
    
    # Populating the graphs
    __nodes_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, NODES, PREDS, SORTINFO)
    __links_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, LINKS, NODES)

    return defaultGraph


def __nodes_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, NODES, PREDS, SORTINFO):
    """
    Creates in the graphs the nodes of DMRS predications and their properties.

    Args:
        d: a PyDelphin DMRS instance to be converted into RDF format
        dmrsGraph: a rdflib Graph where the DMRS triples will be put.
        defaultGraph: the conjunctive graph of the profile
        DMRSI: the node of the DMRS instance being converted
        NODES: the URI namespace dedicated to DMRS predications
        PREDS: the URI namespace dedicated to predicates
        SORTINFO: the URI namespace dedicated to the sortinfo (morphosemantic information).
    """
    for i in range(len(d.nodes)):
        node = d.nodes[i]
        nodeURI = NODES[f"{node.id}"] #era i, mas não da pra fazer link assim. Rever.
        predURI = PREDS[f"{node.id}"]
        sortinfoURI = SORTINFO[f"{node.id}"]
        
        dmrsGraph.add((nodeURI, RDF.type, DMRS.Node))
        dmrsGraph.add((sortinfoURI, RDF.type, DELPH.SortInfo))

        # Information about the DMRS node
        dmrsGraph.add((DMRSI, DMRS.hasNode, nodeURI))
        dmrsGraph.add((nodeURI, DELPH.hasPredicate, predURI))
        dmrsGraph.add((nodeURI, DELPH.hasSortInfo, sortinfoURI))
        dmrsGraph.add((nodeURI, DMRS.hasId, Literal(node.id))) # review later if this is useful
        dmrsGraph.add((nodeURI, RDFS.label, Literal(f"{delphin.predicate.normalize(node.predicate)}<{node.cfrom},{node.cto}>")))
        #type:
        if node.type is not None:
            #graph.add((nodeIRI, DMRS.cvarsort, DELPH[node.type]))
            dmrsGraph.add((nodeURI, RDF.type, DELPH[node.type]))
            
        # Information about the predicate
        dmrsGraph.add((predURI, DELPH.predText, Literal(delphin.predicate.normalize(node.predicate))))
        if delphin.predicate.is_surface(node.predicate):
            dmrsGraph.add((predURI, RDF.type, DELPH.SurfacePredicate))
        elif delphin.predicate.is_abstract(node.predicate):
            dmrsGraph.add((predURI, RDF.type, DELPH.AbstractPredicate))
        else:
            dmrsGraph.add((predURI, RDF.type, DELPH.Predicate))
            print(f"{node.predicate} is an invalid predicate.")

        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(node.predicate))
        if splittedPredicate[0] is not None:
            dmrsGraph.add((predURI, DELPH.hasLemma, Literal(splittedPredicate[0])))
        if splittedPredicate[1] is not None:
            dmrsGraph.add((predURI, DELPH.hasPos, POS[splittedPredicate[1]]))
        if splittedPredicate[2] is not None:
            dmrsGraph.add((predURI, DELPH.hasSense, Literal(splittedPredicate[2])))    
            
        # lnk
        if node.cfrom is not None:
            dmrsGraph.add((nodeURI, DELPH.cfrom, Literal(node.cfrom)))
        if node.cto is not None:
            dmrsGraph.add((nodeURI, DELPH.cto, Literal(node.cto)))

        # properties / sortinfo
        for prop, val in node.properties.items():
            dmrsGraph.add((sortinfoURI, ERG[prop.lower()], Literal(val.lower())))

        # carg; review later
        if node.carg is not None:
            dmrsGraph.add((nodeURI, DELPH.carg, Literal(node.carg)))

def __links_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, LINKS, NODES):
    """
    Creates in the graphs the nodes of DMRS links and their properties.

    Args:
        d: a PyDelphin DMRS instance to be converted into RDF format
        dmrsGraph: a rdflib Graph where the DMRS triples will be put.
        defaultGraph: the conjunctive graph of the profile
        DMRSI: the node of the DMRS instance being converted
        LINKS: the URI namespace dedicated to DMRS links.
        NODES: the URI namespace dedicated to DMRS predications
    """

    for i in range(len(d.links)):
        link = d.links[i]
        linkURI = LINKS[f"{i}"]
        
        dmrsGraph.add((DMRSI, DMRS.hasLink, linkURI))
        dmrsGraph.add((linkURI, RDF.type, DMRS.Link))
        dmrsGraph.add((linkURI, RDFS.label, Literal(f"{link.role}/{link.post}")))
        
        # the directions
        dmrsGraph.add((linkURI, DMRS.hasFrom, NODES[f"{link.start}"]))
        dmrsGraph.add((linkURI, DMRS.hasTo, NODES[f"{link.end}"]))
        
        # adding roles and posts and creating (just to make sure, maybe remove the last one)
        dmrsGraph.add((linkURI, DMRS.hasRole, DMRS[link.role.lower()]))
        dmrsGraph.add((linkURI, DMRS.hasScopalRelation, DMRS[link.post.lower()]))
        dmrsGraph.add((DMRS[link.post.lower()], RDF.type, DMRS.ScopalRelation))
        dmrsGraph.add((DMRS[link.role.lower()], RDF.type, DMRS.Role)) 


