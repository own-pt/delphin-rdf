from _NodeExpression import PREDICATE
from _NodeExpression import NodeExpression
from _QEQExpression import QEQExpression

from _OperationExpression import OPERATOR_CON as CONOP
from _OperationExpression import OPERATOR_DIS as DISOP
from _OperationExpression import OPERATOR_NEG as NEGOP

NEQLEVEL = 20
QEQLEVEL = 6

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
    # * qual a utilizade/significado de aux/temp
    # * qual a substituto para "SELECT GRAPH"
    # * completar e entender _to_sparql_body
    # * maneira de atualizar/ajustar a query
    # * entender melhor o sparql gerado
    # * adicionar a feature de ordenamento
    # * adicionar unique_filter feature

    # initialize output with prefixes
    sparql = "\n".join(prefixes)

    # generate structures sparql and
    # converts it to a string sparql
    auxiliar_variables = []         # a container for generated variables
    auxiliar_variables += ["aux0", "aux1", "aux2", "aux3", "aux4", "aux5"]
    sparql_where = _to_sparql(expression,auxiliar_variables).to_sparql_string()

    # add other elements
    sparql += "SELECT \n\t?GRAPH "
    for var in auxiliar_variables:
        sparql += f"?{var} "
    sparql += "\nWHERE\n\t{" + sparql_where+" }"

    # add_unique_filter

    return sparql

def _to_sparql(expression, temp):
    """
    Modela a query-tree como uma Weighted String,
    o que é feito recursivamente.
    """
    if expression.is_leaf():
        return _to_sparql_node(expression, temp)
    return _to_sparql_operator(expression, temp)

def _to_sparql_node(expression, temp):
    """"""
    
    # * needs a complete definition
    # * define a general parser based on
    # classes: MRS.to_sparql(temp)

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

    qeqs = expression.qeqs
    output = ["?{} mrs:Qeq ?{} .".format(*qeq) for qeq in qeqs]
    output = "\n".join(output)

    return WeightedString(QEQLEVEL, 0, output)

def _to_sparql_body(expression,temp):
    """"""
    # * need to understand almost everything
    # * review vocabularie

    return WeightedString(QEQLEVEL, 0, expression.expression)

def _level(name):
    """"""
    pass

def _add_data_value(id,level,value,type):
    """"""
    pass

def _to_sparql_operator(expression, temp):
    """"""
    # * meaning of a Weighted String
    # * code reuse on OROP
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
        in this second case, define the weight
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
            else: weight += value.weight
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
        Converte a Weighted String, na forma sparql
        representada. Para isso considera aspectos
        como peso, nivel valor e valores.
        """
        # * better readability by newlines
        
        # if a node/leaf return the value
        if not self.value == None: return self.value
        
        # othewise, sorts and calls recursively
        self.values = sorted(self.values, key=self._compare_key)
        return " ".join([ws.to_sparql_string() for ws in self.values])