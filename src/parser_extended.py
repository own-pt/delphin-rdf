from delphin import ace
from delphin import eds
from delphin.codecs import eds as edsnative

# defining rdf templates
import templates_extended as tmp

def vars_to_rdf(variables):
    """
    Turns mrs variables into rdf descriptions. At this first
    description, we use only the names for description.

    variables: a list of defined variabes:. Note that in mrs
    both, nodes and handles are pushed as varibles.
    """

    nodes = [v for v in variables.keys() if not v[0]=="h"]
    nodes = [tmp.node.format(var=node) for node in nodes]

    handles = [v for v in variables.keys() if v[0]=="h"]
    handles = [tmp.handle.format(var=handle) for handle in handles]
    
    return {"nodes": nodes, "handles":handles}
    
def rels_args_to_rdf(index, args, m):
    """
    Turns mrs args into rdf descriptions defined in template.

    args: a dicionary of arguments. Consider keys as holes
    and values as the arguments of each hole.
    """

    res = []
    for hole in args:
        if hole == "ARG0": continue
        
        arg = args[hole]
        # defines the type of argument
        try:
            arg_type = type(eval(arg.title()))
            if arg_type == int: template = tmp.rel_args_int
            elif arg_type == bool: template = tmp.rel_args_boo
            elif arg_type == float: template = tmp.rel_args_dec
            
            # default type in case of other type
            else: template = tmp.rel_args_def
        except:
            if arg in m.variables: template = tmp.rel_args_var
            else: template = tmp.rel_args_str

        res.append(template.format(
            i = index,
            j = len(res) + 1,
            arg = arg))
        
    return res 
        
def rels_to_rdf(rels, m):
    """
    Turns mrs RELS into rdf descriptions given by the
    rel template defined in acordance with vocabulary.
    
    rels: a list of EPs objects defined for the text
    m: the delphin.mrs object generated for the text
    """

    res = []
    for i in range(len( rels)):
        rel = rels[i]
        args = rels_args_to_rdf(i + 1, rel.args, m)

        # formats using template
        res.append(tmp.rel.format(
            i = i + 1,
            label = rel.label,
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
        res.append(tmp.hcons.format(
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
        res.append(tmp.hcons.format(
            i = i + 1,
            harg = cons.left,
            larg = cons.right,
            rel = cons.relation))

    return res


def parse(text, grm):
    """
    Fomats the final rdf receiving all declarations defined
    in main.

    text: the original text (phare) parsed
    prefixes: list of rdf prefixes used 
    nodex: list of rdf nodes declaration
    handles: list of rdf handles declaration
    rels: list of rdf relation desciptions
    hcons: list of rdf hcons desciptions
    icons: list of rdf icons desciptions
    """

    response = ace.parse(grm, text)
    m = response.result(0).mrs()

    # parse nodes, handles 
    vars = vars_to_rdf(m.variables)
    nodes = vars["nodes"]
    handles = vars["handles"]

    # parse rels
    rels = rels_to_rdf(m.rels, m)

    # parse hcons
    hcons = hcons_to_rdf(m.hcons)

    # parse icons
    icons = icons_to_rdf(m.icons)

    return tmp.main.format(
        text = text,
        nodes = "\n".join(nodes),
        handles = "\n".join(handles),
        rels = "\n".join(rels),
        hcons = "\n".join(hcons),
        icons = "\n".join(icons))