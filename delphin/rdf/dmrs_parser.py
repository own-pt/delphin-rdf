from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace

import delphin  
from delphin import dmrs

# some usefull namespaces
DMRS = Namespace("http://www.delph-in.net/schema/dmrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DMRSTYPE = Namespace("http://www.delph-in.net/schema/dmrs#type#")

def __nodes_to_rdf__(d, graph, dmrsi, NODES):
    """
    Creates nodes of variables and nodes specifying their properties.

    d - a delphin dmrs instance to be parsed into RDF format.
    
    dmrsi - the dmrs iri of the specific instance being parsed.

    graph - and rdflib graph that is used to store the DMRS as RDF
    representation.

    NODES - the URI namespace dedicated to nodes.
    """
    for i in range(len(d.nodes)):
        node = d.nodes[i]
        nodeIRI = NODES["node{}".format(node.id)] #era i, mas não da pra fazer link assim. Rever.
        nodePredIRI = nodeIRI + "#predicate"
        
        #putting it's id 
        graph.add((nodeIRI, DMRS.hasId, Literal(node.id)))
        
        #Instantiate the Node and putting into the DMRS
        graph.add((nodeIRI, RDF.type, DMRS.Node))
        graph.add((dmrsi, DMRS.hasNode, nodeIRI))
        
        #typing the predicate and associating with the node
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(node.predicate))
        if delphin.predicate.is_surface(node.predicate):
            graph.add((nodePredIRI, RDF.type, DMRS.SurfacePredicate))
            graph.add((nodePredIRI, DMRS.hasLemma, Literal(splittedPredicate[0])))
        elif delphin.predicate.is_abstract(node.predicate):
            graph.add((nodePredIRI, RDF.type, DMRS.AbstractPredicate))
            graph.add((nodePredIRI, DMRS.hasName, Literal(splittedPredicate[0])))
        else:
            graph.add((nodePredIRI, RDF.type, DMRS.Predicate))
            print("An invalid predicate")
            
        if splittedPredicate[1] is not None:
            graph.add((nodePredIRI, DMRS.hasPos, DMRS[splittedPredicate[1]]))
        if splittedPredicate[2] is not None:
            graph.add((nodePredIRI, DMRS.hasSense, Literal(splittedPredicate[2])))    
            
        graph.add((nodeIRI, DMRS.hasPredicate, nodePredIRI))
        
        #lnk
        if node.cfrom is not None:
            graph.add((nodeIRI, DMRS.cfrom, Literal(node.cfrom)))
        if node.cto is not None:
            graph.add((nodeIRI, DMRS.cto, Literal(node.cto)))

        #properties / sortinfo
        for prop, val in node.properties.items():
            graph.add((nodeIRI, DMRS[prop.lower()], Literal(val.lower())))
        
        #type:
        if node.type is not None:
            graph.add((nodeIRI, DMRS.cvarsort, DMRSTYPE[node.type]))
            
        # carg
        if node.carg is not None:
            graph.add((nodeIRI, DMRS.carg, Literal(node.carg)))


def __links_to_rdf__(d, graph, dmrsi, NODES, LINKS):
    """
    Creates the links of a DMRS in the RDF graph.

    d - a delphin dmrs instance to be parsed into RDF format.
    
    dmrsi - the dmrs iri of the specific instance being parsed.

    graph - and rdflib graph that is used to store the DMRS as RDF
    representation.

    NODES - the URI namespace dedicated to nodes.

    LINKS - the URI namespace dedicated to links.
    """

    for i in range(len(d.links)):
        link = d.links[i]
        linkIRI = LINKS["link{}".format(i)]
        
        #declaring the link node
        graph.add((linkIRI, RDF.type, DMRS.hasLink))
        graph.add((dmrsi, DMRS.hasLink, linkIRI))
        
        #the directions
        graph.add((linkIRI, DMRS.hasFrom, NODES["node{}".format(link.start)]))
        graph.add((linkIRI, DMRS.hasTo, NODES["node{}".format(link.end)]))
        
        #adding roles and posts and creating (just to make sure, maybe remove the last one)
        graph.add((linkIRI, DMRS.hasRole, DMRS[link.role.lower()]))
        graph.add((linkIRI, DMRS.hasScopalRelation, DMRS[link.post.lower()]))
        graph.add((DMRS[link.post.lower()], RDF.type, DMRS.ScopalRelation))
        graph.add((DMRS[link.role.lower()], RDF.type, DMRS.Role)) 


def dmrs_to_rdf(d, prefix: str, identifier, iname="dmrsi#dmrs", graph=None, out=None, text=None, format="turtle"):
    """
    Parses a pydelphin DMRS into RDF representation.

    d - a delphin DMRS instance to be parsed into RDF format.

    prefix - the IRI to be prefixed to the RDF formated DMRS.

    identifier - an string or a list of strings identifying
    the DMRS. It should be unique, possibly using a composite
    identifier, given in list.
    For instance one may use it as [textid, dmrs-id] if the
    same text admits various mrs interpretations.

    iname - the dmrs instance name (the dmrs as RDF node name)
    to be used. As default, it is "dmrsi#dmrs".

    graph - and rdflib graph. If given, uses it to store the
    dmrs as RDF representation.

    out - filename to serialize the output into.

    text - the text that is represented in dmrs as RDF. 

    format - file format to serialize the output into.
    """

    if not graph: graph = Graph()
    if type(identifier) == list:
        identifier = "/".join(identifier)

    namespace = prefix + "/" + identifier + "/"

    dmrsi = URIRef(namespace + iname)
    graph.add((dmrsi, RDF.type, DMRS.DMRS))

    NODES = Namespace(namespace + "nodes#")
    LINKS = Namespace(namespace + "links#")

    __nodes_to_rdf__(d, graph, dmrsi, NODES)
    
    #Adding top
    graph.add((dmrsi, DMRS['hasTop'], NODES["node{}".format(d.top)]))
    #Adding index
    graph.add((dmrsi, DMRS['hasTop'], NODES["node{}".format(d.index)]))

    __links_to_rdf__(d, graph, dmrsi, NODES, LINKS)

    # add text as one graph node if it's given
    if text: graph.add((dmrsi, DMRS.text, Literal(text)))
    # serializes graph if given an output file
    if out: graph.serialize(destination=out, format=format)

    return graph
