from _TempData import TempData

from _NodeExpression import NodeExpression

from _QEQExpression import QEQExpression

from _OperationExpression import OPERATOR_CON as CONOP
from _OperationExpression import OPERATOR_DIS as DISOP
from _OperationExpression import OPERATOR_NEG as NEGOP

ID_LEVEL = 5
QEQLEVEL = 6
TYPE_LEVEL = 7
NEQLEVEL = 20

TOP = "top"
LBL = "lbl"
CARG = "carg"
ROLE = "properties"
PREDICATE = "predicate"


prefixes = (
    '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .',
    '@prefix delph: <http://www.delph-in.net/schema/> .',
    '@prefix erg: <http://www.delph-in.net/schema/erg#> .',
    '@prefix mrs: <http://www.delph-in.net/schema/mrs#> .',
    '@prefix pos: <http://www.delph-in.net/schema/pos#> .',
    '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .', '\n')

def _to_sparql_structure(expression, ordered = False):
    """
    - initialize(output) : prefixos
    - toSparql(parsed, aux) : recusivo; operacao ou folha
        - toSparqlOperator()
        - toSparqlNode()
    - adicionamos sufixos, ordenacao, variaveis, etc
    """
    # * qual o substituto para "SELECT GRAPH"
    # * completar e entender _to_sparql_body
    # * maneira de atualizar/ajustar a query
    # * entender melhor o sparql gerado
    # * adicionar a feature de ordenamento
    # * adicionar unique_filter feature

    # initialize output with prefixes
    sparql = "\n".join(prefixes)

    # generate structures sparql and
    # converts it to a string sparql
    variables = TempData()
    sparql_where = _to_sparql(expression,variables).to_sparql_string()

    # add other elements
    # sparql += "SELECT \n\t?GRAPH "
    sparql += "SELECT ?graph "
    for var in variables.variables:
        sparql += f"?{var} "
    sparql += "WHERE {" + sparql_where + " } "
    
    # * add_unique_filter and other features

    sparql += "GROUP BY GROUP BY ?graph"

    return sparql

def _to_sparql(expression, temp):
    """
    Modela a query-tree como uma WeightedString,
    o que é feito recursivamente.
    """
    if expression.is_leaf():
        return _to_sparql_node(expression, temp)
    return _to_sparql_operator(expression, temp)

def _to_sparql_node(expression, temp):
    """"""

    # if a QEQExpresion
    if type(expression) == QEQExpression:
        return _to_sparql_qeqs(expression,temp)

    # if a NodeExpression
    if type(expression) == NodeExpression:
        return _to_sparql_body(expression,temp)
    
    return WeightedString(0,0,None)

def _to_sparql_qeqs(expression,temp):
    """"""
    # * use vocalbularie definition of QEQ relations
    # * meaning constants of such as QEQLEVEL

    qeqs = expression.qeqs
    output = ["?{} mrs:Qeq ?{} .".format(*qeq) for qeq in qeqs]
    output = " ".join(output)

    return WeightedString(QEQLEVEL, 0, output)

def _to_sparql_body(expression,temp):
    """
    Parses the body of a expression: the nodes
    aside from HConstraints or IConstraints.
    """
    # * understand _to_sparql_body/toSparqlNode
    # * review vocabularies to transcribe
    # * TempData to a more informative name
    # * what are CARG, TOP, etc
    # * roles may receive a new_variable

    out = []
    id_ = temp.new_variable()
    temp.variables.append(id_)

    # processing PREDICATE
    if PREDICATE in expression.values:
        # * back here to implement
        predicate = expression.values[PREDICATE]
        out += _add_data_value(id_, _level(PREDICATE), predicate, PREDICATE)
    
    # processing CARG
    if CARG in expression.values:
        # * back here to implement
        carg = expression.values[CARG]
        out += _add_data_value(id_, _level(carg), carg, carg)

    # # processing TOP
    # if TOP in expression.values:
    #     # * understand original code
    #     s = f"?{id} {namespace_prefix()}:{TOP} \"true\"^^xsd:boolean"
    #     out += _add_data_value(id, _level(carg), carg, carg)
    
    # adding roles
    for role in expression.roles:
        if role[1] == None:
            role[1] = temp.new_variable()
        temp.variables.append(role[1])
        out.append(_add_role(id_, role, "role"))

        mrs_type = _add_mrs_type(role[1])
        if not mrs_type == None: out.append(mrs_type)

    # processing ID
    if not expression.id == None:
        s = f"?{id_} {namespace_prefix()}:{LBL} ?{expression.id}"
        out.append(WeightedString(ID_LEVEL, 0, s))

        mrs_type = _add_mrs_type(role[1])
        if not mrs_type == None: out.append(mrs_type)

    return WeightedString(values=out)

def namespace_prefix():
    """"""
    # * add new vocabularies definitions
    return "mrs"

def _level(name):
    """"""
    # map is just a simplification
    map_ = {CARG:1, PREDICATE:2,TOP:3,ROLE:4}
    return map_[name]

def _add_mrs_type(variable):
    """"""
    # * care about the new vocabulary

    # a generated variable
    if variable[:3] == "aux" and variable[3:].isnumeric():
        return None

    first = variable[0]
    # not a mrs type
    if first not in ["X","E","I","P","H"]:
        return None

    # mount a type constraint
    out = f"?{variable} rdfs:type {namespace_prefix()}:{first} ."
    return WeightedString(TYPE_LEVEL, 0, out)

def _add_role(id, role, topEdge):
    """"""
    # * revisit for idexed expressions
    # * better understand different cases
    # * understand use of regular expressions

    var = role[1]
    rel = role[0].lower()
    regexp = _is_regexp(rel)

    # differs if marker "+" is in role name
    if not "+" in rel:
        rel = f"{namespace_prefix()}:{rel}"
    else:
        rel = f"<{namespace_prefix()}#{rel}>"

    rel = f"?{id} {rel} ?{var} ."
    return WeightedString(_level(ROLE),1,rel)

def _add_data_value(id,level,value,type_):
    """"""
    # * return to understando about the regexp
    # * original code handles possible quoted

    # out = []
    regexp = _is_regexp(value)

    # returns a void list
    if regexp and len(value) == 1: return out
    
    s = f"?{id} {namespace_prefix()}:{type_} \"{value}\"^^xsd:string ."
    return [WeightedString(level,1,s)]

def _is_regexp(expression):
    return False

def _to_sparql_operator(expression, temp):
    """"""
    # * code reuse on DISOP
    # * meaning of a WeightedString
    # * ordering meaning in DISOP and CONOP
    # * code reuse for lambda x: (x.level,x.weight)

    # NEGOP tranforms and add FILTER
    if expression.operator == NEGOP:
        w_child = _to_sparql(expression.left, temp)
        output = f"FILTER NOT EXISTS { {w_child.to_sparql_string()} }"

        return WeightedString(NEQLEVEL,0,output)
    
    # otherwise parses both sides
    left = _to_sparql(expression.left,temp)
    right = _to_sparql(expression.right,temp)

    # DISOP 
    if expression.operator == DISOP:
        if left.value == None:
            # sorts by level than weight
            left.values = sorted(left.values, left._compare_key)
            left.value = left.to_sparql_string()
            # sets largest level from values
            left.level = left.values[-1].level
        
        if right.value == None:
            # sorts by level than weight
            right.values = sorted(right.values, key=right._compare_key)
            right.value = right.to_sparql_string()
            # sets largest level from values
            right.level = right.values[-1].level
        
        _expression = sorted([left,right], key=right._compare_key)
        return WeightedString(
            left._level(_expression),
            left.weight + right.weight,
            left._to_union_string(_expression))

    # CONOP considers the agregation
    _expression = []

    if left.value == None: _expression += left.values
    else: _expression.append(left)
    if right.value == None: _expression += right.values
    else: _expression.append(right)

    return WeightedString(values=_expression)
    
class WeightedString:
    def __init__(self,level=None,weight=None,value=None,values=None):
        """
        A Weighted String contains an expression
        os a sequence of Weighted Strings, wich,
        in this second case, defines the weight
        """

        self.level = level
        self.value = value
        self.weight = weight
        self.values = values
        # two ways to describe a WS
        if not values == None:
            self.weight = self._weight(values)
    
    def _compare_key(self,x): return (x.level,x.weight)

    def _weight(self,values):
        """
        A Weighted String's weight is given as a
        reunion of it's values/items' weights
        """
        weight = 0
        for value in values:
            if not value.values == None:
                weight += self._weight(value.values)
            else:
                weight += value.weight
        return weight
    
    def _level(self, values):
        """
        Search the least level, where the level
        is given by it's values
        """
        # * De onde vem, o que significa 110?

        level = 110
        for value in values:
            l = value.level
            if l == 0: l = self._level(value)
            if l < level: level = l
        return level

    def _to_union_string(self,values):
        first = values[0]
        if len(values) == 1: return first.to_sparql_string()

        return f"{ {first.to_sparql_string()} } UNION { {self._to_union_string(values[1:])} }"
    
    def to_sparql_string(self):
        """
        Converte a WeightedString, na forma sparql
        representada. Para isso considera aspectos
        como peso, nivel valor e valores.
        """
        # * better readability by newlines
        
        # if a node/leaf return the value
        if not self.value == None: return self.value
        
        # othewise, sorts and calls recursively
        self.values = sorted(self.values, key=self._compare_key)
        return " ".join([ws.to_sparql_string() for ws in self.values])