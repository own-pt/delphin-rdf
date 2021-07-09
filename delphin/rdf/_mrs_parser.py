from rdflib.graph import Graph
from rdflib.graph import ConjunctiveGraph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace
from rdflib import plugin

import delphin.variable
import delphin.predicate


# some useful namespaces
MRS = Namespace("http://www.delph-in.net/schema/mrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

def mrs_to_rdf(m:delphin.mrs._mrs.MRS, 
                MRSI:rdflib.term.URIRef,
                store:rdflib.plugins.memory.IOMemory=plugin.get("IOMemory", Store)(),
                defaultGraph:rdflib.graph.Graph=None) -> rdflib.plugins.memory.IOMemory:
    """
    Takes a PyDelphin MRS object "m" and serializes it into a named graph inside a store.

    Args:
        m: a delphin mrs instance to be converted into RDF format
        MRSI: URI of the MRS instance being converted
        store: RDFLib IOMemory store to add the graphs. 
        defaultGraph : the default graph of the store. If not given, creates one from the 'store'.

    Inplace function that alters the store with the serialized MRS and return the store as well.
    """
    # Making the arguments behave well:
    if defaultGraph is None:
        defaultGraph = Graph(store, identifier=BNode)

    if defaultGraph.store != store: # Bad function input
        defaultGraph = Graph(store, identifier=BNode)
        print("'defaultGraph' argument not consistent with the 'store' argument. The argument was discarded")

    # MRS graph:
    mrsGraph = Graph(store, identifier=MRSI)

    # Creating the prefix of the MRS elements and relevant namespaces
    insprefix = Namespace(MRSI + '#')
    VARS = Namespace(insprefix + "variable-")
    RELS = Namespace(insprefix + "EP-")
    PREDS = Namespace(insprefix + "predicate-")
    SORTINFO = Namespace(insprefix + "sortinfo-")
    HCONS = Namespace(insprefix + "hcons-")
    ICONS = Namespace(insprefix + "icons-")

    # Adding top and index
    mBNode = BNode()
    mrsGraph.add((mBNode, DELPH['hasTop'], VARS[m.top]))
    mrsGraph.add((mBNode, DELPH['hasIndex'], VARS[m.index]))
    # ALTERNATIVE: ({mrs-node}, DELPH['hasTop'], VARS[m.top]). The issue is that the mrs-node is already the graph identifier
    
    # Populating the graphs
    _vars_to_rdf(m, mrsGraph, VARS, SORTINFO)
    _rels_to_rdf(m, mrsGraph, defaultGraph, MRSI, RELS, PREDS, VARS)
    _hcons_to_rdf(m, mrsGraph, defaultGraph, MRSI, HCONS, VARS)
    _icons_to_rdf(m, mrsGraph, defaultGraph, MRSI, ICONS, VARS)

    return store

def _vars_to_rdf(m, mrsGraph, VARS, SORTINFO):
    """
    Converts the variables of a MRS to the RDF graph

    Args: 
        m: a delphin mrs instance to be converted into RDF format
        mrsGraph: rdflib Graph of a Store of graphs where the MRS triples will be put.
        VARS: the URI namespace dedicated to variables.
        SORTINFO: the URI namespace dedicated to the sortinfo (morphosemantic information).
    """

    for v in m.variables.items():
        if delphin.variable.is_valid(v[0]):
            # typing variables
            if delphin.variable.type(v[0]) != 'h':
                mrsGraph.add((VARS[v[0]], RDF.type, DELPH[delphin.variable.type(v[0])]))
            else :
                mrsGraph.add((VARS[v[0]], RDF.type, MRS['h']))

            # associating the variable to its sortinfo
            mrsGraph.add((VARS[v[0]], DELPH.hasSortInfo, SORTINFO[v[0]]))

            # adding the properties of the variables
            for props in v[1].items():
                mrsGraph.add((SORTINFO[v[0]], ERG[props[0].lower()], Literal(props[1])))
            # it won't be harmful to reassure that the property is defined in ERG, but it'll be like that for now.
        else: # very rare event, should it be removed?
            print("Invalid variable name")

def _rels_to_rdf(m, mrsGraph, defaultGraph, MRSI, RELS, PREDS, VARS):
    """
    Converts the EPs of a MRS to the graph

    Args:
        m: a delphin mrs instance to be converted into RDF format
        mrsGraph: rdflib Graph of a Store of graphs where the MRS triples will be put.
        defaultGraph: the default graph of the Store with the mrsGraph
        MRSI: the node of the MRS instance being converted
        RELS: the URI namespace dedicated to EPs
        PREDS: the URI namespace dedicated to predicates
        VARS: the URI namespace dedicated to variables
    """

    for rel in range(len(m.rels)):
        mrs_rel = m.rels[rel]
        EPNode = RELS[f"{rel}"] #maybe label EPs in a different manner is better because they aren't ordered.
        predNode = PREDS[f"{rel}"]

        defaultGraph.add((MRSI, MRS.hasEP, EPNode))
        mrsGraph.add((EPNode, RDF.type, MRS.ElementaryPredication))
        mrsGraph.add((EPNode, MRS.hasLabel, VARS[mrs_rel.label]))
        # graph.add((rdf_rel, MRS.var, VARS[mrs_rel.iv])) #not needed because ARG0 is already being included at the end of function
            
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(mrs_rel.predicate))
        if delphin.predicate.is_surface(mrs_rel.predicate):
            mrsGraph.add((predNode, RDF.type, DELPH.SurfacePredicate))
        elif delphin.predicate.is_abstract(mrs_rel.predicate):
            mrsGraph.add((predNode, RDF.type, DELPH.AbstractPredicate))
        else: #not(delphin.predicate.is_valid(mrs_rel.predicate))
            print("{} is an invalid predicate.".format(mrs_rel.predicate)) #revise; maybe something stronger.
            mrsGraph.add((predNode, RDF.type, DELPH.Predicate)) #revise

        mrsGraph.add((EPNode, DELPH.hasPredicate, predNode))
        mrsGraph.add((predNode, DELPH.predText, Literal(delphin.predicate.normalize(mrs_rel.predicate))))
        mrsGraph.add((predNode, RDFS.label, Literal(delphin.predicate.normalize(mrs_rel.predicate))))

        if splittedPredicate[0] is not None: #here, lemma = name by now.
            mrsGraph.add((predNode, DELPH.hasLemma, Literal(splittedPredicate[0])))
        
        if splittedPredicate[1] is not None:
            mrsGraph.add((predNode, DELPH.hasPos, POS[splittedPredicate[1]]))
            
        if splittedPredicate[2] is not None:
            mrsGraph.add((predNode, DELPH.hasSense, Literal(splittedPredicate[2])))
        #lnk:
        if mrs_rel.cfrom is not None:
            mrsGraph.add((EPNode, DELPH.cfrom, Literal(mrs_rel.cfrom))) #integer
        if mrs_rel.cto is not None:
            mrsGraph.add((EPNode, DELPH.cto, Literal(mrs_rel.cto))) #integer
     
        # parse arguments
        for hole, arg in mrs_rel.args.items():
            # mrs variables as arguments
            if hole.lower() != "carg" :
                mrsGraph.add((EPNode, MRS[hole.lower()], VARS[arg]))
            else :
                mrsGraph.add((EPNode, DELPH.carg, Literal(arg)))

def _hcons_to_rdf(m, mrsGraph, defaultGraph, MRSI, HCONS, VARS):
    """
    Describes handle constraints "HCONS" in an MRS-RDF format

    Args:
        m: a delphin mrs instance to be converted into RDF format
        mrsGraph: rdflib Graph of a Store of graphs where the MRS triples will be put.
        defaultGraph: the default graph of the Store with the mrsGraph
        MRSI: the node of the MRS instance being converted
        HCONS: the URI namespace dedicated to handle constraints
        VARS: the URI namespace dedicated to variables
    """

    for id_hcons in range(len(m.hcons)):
        mrs_hcons = m.hcons[id_hcons]
        HCONSNode = HCONS[f"{id_hcons}"]
        
        # adds hcons to graphs
        defaultGraph.add((MRSI, MRS.hasHcons, HCONSNode))
        mrsGraph.add((HCONSNode, RDF.type, MRS[mrs_hcons.relation.capitalize()]))
        mrsGraph.add((HCONSNode, MRS.highHcons, VARS[mrs_hcons.hi]))
        mrsGraph.add((HCONSNode, MRS.lowHcons, VARS[mrs_hcons.lo]))

def _icons_to_rdf(m, mrsGraph, defaultGraph, MRSI, ICONS, VARS):
    """
    Describes individual constraints "ICONS" in MRS-RDF format

    Args:
        m: a delphin mrs instance to be converted into RDF format
        mrsGraph: rdflib Graph of a Store of graphs where the MRS triples will be put.
        defaultGraph: the default graph of the Store with the mrsGraph
        MRSI: the node of the MRS instance being converted
        ICONS: the URI namespace dedicated to individual constraints
        VARS: the URI namespace dedicated to variables
    """

    for id_icons in range(len(m.icons)):
        mrs_icons = m.icons[id_icons]
        ICONSNode = ICONS[f"{id_icons}"]
        
        # adds icons to graphs
        defaultGraph.add((MRSI, MRS.hasIcons, ICONSNode))
        mrsGraph.add((ICONSNode, RDF.type, ERG[mrs_icons.relation]))
        mrsGraph.add((ICONSNode, MRS.leftIcons, VARS[mrs_icons.left])) # should be revisited
        mrsGraph.add((ICONSNode, MRS.rightIcons, VARS[mrs_icons.right])) # should be revisited

        # by now, the ICONSs seems to be grammar-specific
        # and this relation must be defined in ERG as an icons.
        # As we don't have an exhaustive list of the possible icons in ERG (and any other grammar),
        # we'll create on the final graph those icons. This is provisory
        defaultGraph.add((ERG[mrs_icons.relation], RDF.type, RDFS.Class))
        defaultGraph.add((ERG[mrs_icons.relation], RDFS.subClassOf, MRS.Icons))