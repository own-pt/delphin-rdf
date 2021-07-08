def profile_to_mrs_rdf(
        profile_path:str, 
        prefix:str, 
        iname:str ="mrs", 
        store:rdflib.plugins.memory.IOMemory=plugin.get("IOMemory", Store)()) -> rdflib.plugins.memory.IOMemory:
    """
    Takes a path to a profile and a RDFLib IOMemory store to serialize the profile into the store.
    
    Args:
        profile_path: a path to a profile to be serialized
        prefix: the URI to be prefixed to the RDF formated MRS
        iname: the mrs instance name (the mrs as RDF node name)
            to be used.
        graph: rdflib Graph. If given, uses it to store the MRS
            representation in RDF.
        store: RDFLib IOMemory store to add the graphs.

    Returns the RDFLib IOMemory store with the added graphs.
    """
    
    # normalizing prefix:
    prefix.rstrip('/')
        
    # loading profile
    ts = itsdb.TestSuite(profile_path)
        
    # The default graph and the profile uri 
    PROFILE = URIRef(prefix)
    defaultGraph = Graph(store, identifier=BNode()) # BNode or BNode()?
    graph.add((PROFILE, RDF.type, DELPH.Profile))
    
    # iterating over results:
    for (parse_id, result_id, text, mrs_string) in tsql.select('parse-id result-id i-input mrs', ts):
        ITEM = URIRef(f"{prefix}/{parse_id}") # The item part may be redundant, maybe iterate before the itens
        RESULT = URIRef(f"{prefix}/{parse_id}/{result_id}")
        MRS = URIRef(f"{prefix}/{parse_id}/{result_id}/{iname}")
        
        # adding types:
        graph.add((ITEM, RDF.type, DELPH.Item))
        graph.add((RESULT, RDF.type, DELPH.Result))
        graph.add((MRS, RDF.type, MRS.MRS))
        
        # Associating text to item:
        graph.add((ITEM, DELPH.hasText, Literal(text)))
        
        _mrs_to_rdf(simplemrs.decode(mrs_string), 
                    Namespace(MRS+'#'), 
                    Graph(store, identifier=MRS), 
                    defaultGraph)
#         mrsgraph = Graph(store, identifier=MRS)
#         mrsgraph = _mrs_to_rdf(simplemrs.decode(mrs_string), Namespace(MRS+'#'), mrsgraph)

def _mrs_to_rdf(m:delphin.mrs._mrs.MRS, 
                insprefix:rdflib.namespace.Namespace, 
                mrsGraph:rdflib.graph.Graph, 
                defaultGraph:rdflib.graph.Graph) -> rdflib.graph.Graph:
    """
    Takes a PyDelphin MRS object "m" and serializes it into a graph (usually named).

    Args:
        m: a delphin mrs instance to be converted into RDF format
        insprefix: the prefix of the MRS elements
        mrsGraph: rdflib Graph of a Store of graphs where the MRS triples will be put. 
        defaultGraph : the default graph of the store
    Inplace function that alters mrsGraph and defaultGraph to construct the Graph Store.
    """
    # Adding top and index
    graph.add((BNode(), DELPH['hasTop'], VARS[m.top]))
    graph.add((BNode(), DELPH['hasIndex'], VARS[m.index]))
    # ALTERNATIVE: ({mrs-node}, DELPH['hasTop'], VARS[m.top]). The issue is that the mrs-node is already the graph identifier
    
    VARS = Namespace(namespace + "variable-")
    RELS = Namespace(namespace + "EP-")
    SORTINFO = Namespace(namespace + "EP-")
    HCONS = Namespace(namespace + "hcons-")
    ICONS = Namespace(namespace + "icons-")
    
    _vars_to_rdf(m, defaultGraph, VARS)
    _rels_to_rdf(m, mrsGraph, defaultGraph, RELS, VARS)
    _hcons_to_rdf(m, graph, mrsi, HCONS, VARS)
    _icons_to_rdf(m, graph, mrsi, ICONS, VARS)

def _vars_to_rdf(m, defaultGraph, VARS):
    pass

def _rels_to_rdf(m, defaultGraph, VARS):
    pass

def _hcons_to_rdf(m, defaultGraph, VARS):
    pass

def _icons_to_rdf(m, defaultGraph, VARS):
    pass

