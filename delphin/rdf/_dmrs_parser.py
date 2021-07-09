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
                store:rdflib.plugins.memory.IOMemory=plugin.get("IOMemory", Store)(),
                defaultGraph:rdflib.graph.Graph=None) -> rdflib.plugins.memory.IOMemory:
    """
    Takes a PyDelphin DMRS object "d" and serializes it into a named RDF graph inside a store.
    
    Args:
        d: a PyDelphin DMRS instance to be converted into RDF format
        DMRSI: URI of the DMRS instance being converted
        store: RDFLib IOMemory store to add the graphs. 
        defaultGraph : the default graph of the store. If not given, creates one from the 'store'.
    Inplace function that alters the store with the serialized DMRS and return the store as well.
    """

    # Making the arguments behave well:
    if defaultGraph is None:
        defaultGraph = Graph(store, identifier=BNode())

    if defaultGraph.store != store: # Bad function input
        defaultGraph = Graph(store, identifier=BNode())
        print("'defaultGraph' argument not consistent with the 'store' argument. The argument was discarded")

    # DMRS graph:
    dmrsGraph = Graph(store, identifier=DMRSI)

    # Creating the prefix of the DMRS elements and relevant namespaces
    insprefix = Namespace(DMRSI + '#')
    NODES = Namespace(insprefix + "node-")
    LINKS = Namespace(insprefix + "link-")
    PREDS = Namespace(insprefix + "predicate-")
    SORTINFO = Namespace(insprefix + "sortinfo-")

    #creating the instance URI and the namespaces
    dmrsi = URIRef(namespace + iname)
    graph.add((dmrsi, RDF.type, DMRS.DMRS))
    NODES = Namespace(namespace + "node-")
    LINKS = Namespace(namespace + "link-")
    
    # Adding top and index
    dBNode = BNode()
    dmrsGraph.add((dBNode, DELPH['hasTop'], NODES[d.top]))
    dmrsGraph.add((dBNode, DELPH['hasIndex'], NODES[d.index]))
    # ALTERNATIVE: ({dmrs-node}, DELPH['hasTop'], VARS[m.top]). The issue is that the dmrs-node is already the graph identifier


    # creating the prefixes of the output
    # graph.bind("dmrs", DMRS)
    # graph.bind("delph", DELPH)
    # graph.bind("erg", ERG)
    # graph.bind("pos", POS)
    
    # Populating the graphs
    __nodes_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, NODES, PREDS, SORTINFO)
    __links_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, LINKS, NODES)

    return store


def __nodes_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, NODES, PREDS, SORTINFO):
    """
    Creates in the graphs the nodes of DMRS predications and their properties.

    Args:
        d: a PyDelphin DMRS instance to be converted into RDF format
        dmrsGraph: rdflib Graph of a Store of graphs where the DMRS triples will be put.
        defaultGraph: the default graph of the Store with the dmrsGraph
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
        defaultGraph.add((DMRSI, DMRS.hasNode, nodeURI))
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
            graph.add((nodeURI, DELPH.carg, Literal(node.carg)))


def __links_to_rdf__(d, dmrsGraph, defaultGraph, DMRSI, LINKS, NODES):
    """
    Creates in the graphs the nodes of DMRS links and their properties.

    Args:
        d: a PyDelphin DMRS instance to be converted into RDF format
        dmrsGraph: rdflib Graph of a Store of graphs where the DMRS triples will be put.
        defaultGraph: the default graph of the Store with the dmrsGraph
        DMRSI: the node of the DMRS instance being converted
        LINKS: the URI namespace dedicated to DMRS links.
        NODES: the URI namespace dedicated to DMRS predications
    """

    for i in range(len(d.links)):
        link = d.links[i]
        linkURI = LINKS[f"{i}"]
        
        defaultGraph.add((DMRSI, DMRS.hasLink, linkURI))
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


