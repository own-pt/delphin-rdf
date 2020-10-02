from delphin import ace
from delphin import eds
from delphin.codecs import eds as edsnative

# defining rdf templates
#import templates_simplified as tmpt
from templates import Simplified

def vars_to_rdf(variables):
    """
    Turns mrs variables into rdf descriptions. At this first
    description, we use only the names for description.

    variables: a list of defined variabes:. Note that in mrs
    both, nodes and handles are pushed as varibles.
    """

    nodes = [v for v in variables.keys() if not v[0]=="h"]
    nodes = [tmpt.node.format(var=node) for node in nodes]

    handles = [v for v in variables.keys() if v[0]=="h"]
    handles = [tmpt.handle.format(var=handle) for handle in handles]
    
    return {"nodes": nodes, "handles":handles}
    
def rels_args_to_rdf(args):
    """
    Turns mrs args into rdf descriptions defined in template.

    args: a dicionary of arguments. Consider keys as holes
    and values as the arguments of each hole.
    """

    res = []
    for hole, arg in args.items():
        #if hole == "ARG0": continue
        
        # defines the type of argument
        try:
            arg_type = type(eval(arg.title()))
            if arg_type == int: template = tmpt.rel_args_int
            elif arg_type == bool: template = tmpt.rel_args_boo
            elif arg_type == float: template = tmpt.rel_args_dec
            
            # default type in case of other type
            else: template = tmpt.rel_args_def
        except:
            if arg in m.variables: template = tmpt.rel_args_var
            else: template = tmpt.rel_args_str

        res.append(template.format(
            hole = hole,
            arg = arg))
        
    return res 
        
def rels_to_rdf(rels):
    """
    Turns mrs RELS into rdf descriptions given by the
    rel template defined in acordance with vocabulary.
    
    rels: a list of EPs objects defined for the text
    m: the delphin.mrs object generated for the text
    """

    res = []
    for i in range(len(rels)):
        rel = rels[i]
        args = rels_args_to_rdf(rel.args)

        # formats using template
        res.append(tmpt.rel.format(
            i = i + 1,
            label = rel.label,
            cfrom = rel.cfrom,
            cto = rel.cto,
            variable = rel.iv,
            predicate = rel.predicate,
            args = "\n".join(args)))
    
    return res

def hcons_to_rdf(hcons):
    """
    Turns mrs HCONS into rdf descriptions givens by the
    hcons template defined in acordance with vocabulary.
    
    hcons: a list of hcons objects defined for the text
    """
    
    res = []
    for i in range(len(hcons)):
        cons = hcons[i]
        
        # formats using template
        res.append(tmpt.hcons.format(
            i = i + 1,
            harg = cons.hi,
            larg = cons.lo,
            rel = cons.relation))

    return res

def icons_to_rdf(icons):
    """
    Turns mrs ICONS into rdf descriptions givens by the
    icons template defined in acordance with vocabulary.
    
    icons: a list of hcons objects defined for the text
    """
    
    res = []
    for i in range(len(icons)):
        cons = icons[i]
        
        # formats using template
        res.append(tmpt.hcons.format(
            i = i + 1,
            harg = cons.left,
            larg = cons.right,
            rel = cons.relation))

    return res


def parse(text, prefix, identifier, grm):
    """
    Fomats the final rdf receiving all declarations defined
    in main.

    text: the original text (phare) parsed
    prefix: URI prefixed to RDF output
    identifier: text/resource identifier
    """

    global m
    global tmpt

    tmpt = Simplified(prefix,identifier)

    response = ace.parse(grm, text)
    m = response.result(0).mrs()

    # parse nodes, handles 
    vars = vars_to_rdf(m.variables)
    nodes = vars["nodes"]
    handles = vars["handles"]

    # parse rels
    rels = rels_to_rdf(m.rels)

    # parse hcons
    hcons = hcons_to_rdf(m.hcons)

    # parse icons
    icons = icons_to_rdf(m.icons)

    return tmpt.main.format(
        text = text,
        nodes = "\n".join(nodes),
        handles = "\n".join(handles),
        rels = "\n".join(rels),
        hcons = "\n".join(hcons),
        icons = "\n".join(icons))