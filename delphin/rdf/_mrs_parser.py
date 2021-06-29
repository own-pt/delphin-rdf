from typing import Union

import rdflib
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace

import delphin  
from delphin import mrs

# some useful namespaces
MRS = Namespace("http://www.delph-in.net/schema/mrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

def _vars_to_rdf(m, graph, VARS):
    """
    Describes variables "VARS" in an MRS-RDF format

    Args: 
        m: a delphin mrs instance to be parsed into RDF format
        graph: rdflib Graph. If given, uses it to store the MRS
            representation in RDF
        VARS: the URI namespace dedicated to variables
    """

    for v in m.variables.items():
        if delphin.variable.is_valid(v[0]):
            # typing variables
            if delphin.variable.type(v[0]) != 'h':
                graph.add((VARS[v[0]], RDF.type, DELPH[delphin.variable.type(v[0])]))
            else :
                graph.add((VARS[v[0]], RDF.type, MRS['h']))

            # adding the properties of the variables
            for props in v[1].items():
                graph.add((VARS[v[0]], ERG[props[0].lower()], Literal(props[1])))
            #maybe it won't be harmful to reassure that the property is defined in ERG, but it'll be like that for now.
        else:
            print("Invalid predicate")
def _rels_to_rdf(m, graph, mrsi, RELS, VARS):
    """
    Describes EPs "RELS" in an MRS-RDF format

    Args:
        m: a delphin mrs instance to be parsed into RDF format
        graph: rdflib Graph. If given, uses it to store the MRS
            representation in RDF
        mrsi: the mrs instance name (the MRS as RDF node name)
        RELS: the URI namespace dedicated to EPs
        VARS: the URI namespace dedicated to variables
    """

    for rel in range(len(m.rels)):
        mrs_rel = m.rels[rel]
        rdf_rel = RELS["EP{rel}".format(rel=rel)] #maybe label EPs in a different manner is better because they aren't ordered.
        pred_rel = RELS["EP{rel}#predicate".format(rel=rel)] #revise

        graph.add((mrsi, MRS.hasEP, rdf_rel))
        graph.add((rdf_rel, RDF.type, MRS.ElementaryPredication))
        graph.add((rdf_rel, MRS.hasLabel, VARS[mrs_rel.label]))
        # graph.add((rdf_rel, MRS.var, VARS[mrs_rel.iv])) #not needed because ARG0 is already being included at the end of function
            
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(mrs_rel.predicate))
        if delphin.predicate.is_surface(mrs_rel.predicate):
            graph.add((pred_rel, RDF.type, DELPH.SurfacePredicate))
        elif delphin.predicate.is_abstract(mrs_rel.predicate):
            graph.add((pred_rel, RDF.type, DELPH.AbstractPredicate))
        else: #not(delphin.predicate.is_valid(mrs_rel.predicate))
            print("{} is an invalid predicate.".format(mrs_rel.predicate)) #revise; maybe something stronger.
            graph.add((pred_rel, RDF.type, DELPH.Predicate)) #revise

        graph.add((rdf_rel, DELPH.hasPredicate, pred_rel))
        graph.add((pred_rel, DELPH.predText, Literal(delphin.predicate.normalize(mrs_rel.predicate))))
        
        if splittedPredicate[0] is not None: #here, lemma = name by now.
            graph.add((pred_rel, DELPH.hasLemma, Literal(splittedPredicate[0])))
        
        if splittedPredicate[1] is not None:
            graph.add((pred_rel, DELPH.hasPos, POS[splittedPredicate[1]]))
            
        if splittedPredicate[2] is not None:
            graph.add((pred_rel, DELPH.hasSense, Literal(splittedPredicate[2])))
        #lnk:
        if mrs_rel.cfrom is not None:
            graph.add((rdf_rel, DELPH.cfrom, Literal(mrs_rel.cfrom))) #integer
        if mrs_rel.cto is not None:
            graph.add((rdf_rel, DELPH.cto, Literal(mrs_rel.cto))) #integer
     
        # parse arguments
        
        for hole, arg in mrs_rel.args.items():
            #if hole == "ARG0": continue
            # arg_type = type(eval(arg.title()))
            # ?
            
            # mrs variables as arguments
            if hole.lower() != "carg" :
                graph.add((rdf_rel, MRS[hole.lower()], VARS[arg]))
            else :
                graph.add((rdf_rel, DELPH.carg, Literal(arg)))
                

def _hcons_to_rdf(m, graph, mrsi, HCONS, VARS):
    """
    Describes handle constraints "HCONS" in an MRS-RDF format

    Args:
        m: a delphin mrs instance to be parsed into RDF format
        graph: rdflib Graph. If given, uses it to store the MRS
            representation in RDF
        mrsi: the mrs instance name (the mrs as RDF node name)
        HCONS: the URI namespace dedicated to HCONSs.
        VARS: the URI namespace dedicated to variables.
    """

    for hcon in range(len(m.hcons)):
        mrs_hcon = m.hcons[hcon]
        rdf_hcon = HCONS["hcons{hcon}".format(hcon=hcon)]
        
        # adds hcon to graph
        graph.add((mrsi, MRS.hasHcons, rdf_hcon))
        graph.add((rdf_hcon, RDF.type, MRS[mrs_hcon.relation.capitalize()]))
        graph.add((rdf_hcon, MRS.highHcons, VARS[mrs_hcon.hi]))
        graph.add((rdf_hcon, MRS.lowHcons, VARS[mrs_hcon.lo]))

        
def _icons_to_rdf(m, graph, mrsi, ICONS, VARS):
    """
    Describes individual constraints "ICONS" in MRS-RDF format

    Args:
        m: a delphin mrs instance to be parsed into RDF format
        graph: rdflib Graph. If given, uses it to store the MRS
            representation in RDF
        mrsi: the mrs instance name (the mrs as RDF node name)
        ICONS: the URI namespace dedicated to ICONSs.
        VARS: the URI namespace dedicated to variables.
    """

    for icon in range(len(m.icons)):
        mrs_icon = m.icons[icon]
        rdf_icon = ICONS["icon{icon}".format(icon=icon)]
        
        # adds icon to graph
        graph.add((mrsi, MRS.hasIcons, rdf_icon))
        # by now, the ICONSs seems to be grammar-specific.
        graph.add((rdf_icon, RDF.type, ERG[mrs_icon.relation]))
        graph.add((rdf_icon, MRS.leftIcons, VARS[mrs_icon.left])) # should be revisited
        graph.add((rdf_icon, MRS.rightIcons, VARS[mrs_icon.right])) # should be revisited

        # this relation must be defined in ERG as an icons
        graph.add((ERG[mrs_icon.relation], RDF.type, RDFS.Class))
        graph.add((ERG[mrs_icon.relation], RDFS.subClassOf, MRS.Icons))
        #This is ad-hoc, will be removed one day.
        #To remove it, we need to have an exhaustive list of the possible icons in ERG (later we must adapt to other grammars).
        

def mrs_to_rdf(
        m:delphin.mrs._mrs.MRS,
        prefix:str,
        identifier:Union[str, list],
        iname:str ="mrsi#mrs",
        graph:rdflib.graph.Graph=None,
        text:str=None) -> rdflib.graph.Graph:
    """
    Parses a pydelphin MRS "m" into an RDF representation.

    Args:
        m: a delphin mrs instance to be parsed into RDF format
        prefix: the URI to be prefixed to the RDF formated MRS
        identifier: an string or a list of strings identifying
            the MRS. It may be composite, given in list
        iname: the mrs instance name (the mrs as RDF node name)
            to be used
        graph: rdflib Graph. If given, uses it to store the MRS
            representation in RDF
        text: the text analized, represented in MRS in "m"

    Returns:
        Graph: containing the RDF representation of "m"
    """
    
    # same graph for different mrs
    if graph is None: graph = Graph()
    if type(identifier) == list:
        identifier = "/".join(identifier)

    # creating the namespaces for this MRS instance
    namespace = prefix + "/" + identifier + "/"
    mrsi = URIRef(namespace + iname)
    graph.add((mrsi, RDF.type, MRS.MRS))
    VARS = Namespace(namespace + "variables/")
    RELS = Namespace(namespace + "rels/")
    HCONS = Namespace(namespace + "hcons/")
    ICONS = Namespace(namespace + "icons/")
    
    # creating the prefixes of the output
    graph.bind("mrs", MRS)
    graph.bind("delph", DELPH)
    graph.bind("erg", ERG)
    graph.bind("pos", POS)
    
    # creating the RDF triples
    _vars_to_rdf(m, graph, VARS)
    _rels_to_rdf(m, graph, mrsi, RELS, VARS)
    _hcons_to_rdf(m, graph, mrsi, HCONS, VARS)
    _icons_to_rdf(m, graph, mrsi, ICONS, VARS)
    # adding top
    graph.add((mrsi, DELPH['hasTop'], VARS[m.top]))
    # adding index
    graph.add((mrsi, DELPH['hasIndex'], VARS[m.index]))

    # add text as one graph node if it's given
    if text is not None:
        graph.add((mrsi, DELPH.text, Literal(text)))

    return graph
