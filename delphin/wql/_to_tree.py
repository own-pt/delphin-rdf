import re

from _QEQExpression import QEQExpression
from _QEQExpression import QEQ_BGN
from _QEQExpression import QEQ_END

from _NodeExpression import NodeExpression

from _OperationExpression import OperationExpression
from _OperationExpression import OPERATOR_ANY as ANYOP
from _OperationExpression import OPERATOR_CON as CONOP
from _OperationExpression import OPERATOR_DIS as DISOP
from _OperationExpression import OPERATOR_NEG as NEGOP

def tree_to_str(expression, n=0):
    output = _tree_to_str(expression, n).rstrip()
    # prefix = "-------------------------------------------------"
    # prefix = "##################################################"
    prefix = ""

    return "\n".join([prefix,output,prefix])

def _tree_to_str(expression, n=0, prefix=None):
    output = ""
    prefix = "\t"*n if prefix==None else prefix
    try:
        # expression is a NEGATION
        if expression.operator == NEGOP:
            output += _tree_to_str(expression.right,n+1,"\r"+prefix+expression.operator+"\t")
        # expression is a CON / DIS
        elif expression.operator in ANYOP:
            output += _tree_to_str(expression.left,n+1)
            output += prefix + expression.operator + "\n"
            output += _tree_to_str(expression.right,n+1)
    except Exception:
        # expression is a NODE/LEAF
        output += prefix + expression.expression + "\n"
    return output

def _parse(query:str):
    """"""
    
    # strip blank spaces
    query.strip()
    
    # parses QEQs separately if given
    bgn = None
    end = None
    qeqs_member = None
    if query.endswith(QEQ_END):
        bgn = query.rfind(QEQ_BGN)
        end = query.rfind(QEQ_END)
        qeqs_member = query[bgn+1:end]
    
    # parses BODY separately if given
    body_member = query[0:bgn].strip()
    body_member = _format(body_member)
    body_member = _recognize(body_member)

    if qeqs_member == None:
        return body_member

    # conjunction of both expressions
    qeqs_member = QEQExpression(qeqs_member)

    out_expression=OperationExpression(CONOP, body_member, qeqs_member)
    return out_expression

def _format(query:str):
    # * what about quote "\\\\" replacement
    # * possible use Regular Expressions instead
    # * in the original code the supress operator "\" is not implemented
    # * question about the used definition of in/out
    # * definition of problems opening and closing brackets

    # replace repeated unecessary whitespaces
    query = re.sub(r'\s+', ' ', query)
    query = re.sub(r'(?<=[\[\{|&,!]) ', '', query)
    query = re.sub(r' (?=[\]\}|&,!])', '', query)
    query = re.sub(r'\\\\', '\\\\', query)
    query = query.lstrip()
    
    # format operations to standard
    query = re.sub(r'\&', CONOP, query)
    query = re.sub(r'\|', DISOP, query)
    query = re.sub(r'\!', NEGOP, query)

    # searchs for problems with the brackets
    if re.search(r'(\[[^\].]*\{[^\}.]*\]|\{[^\}.]*\[[^\].]*\})', query):
        raise Exception("Check opening and closing the brackets!")
    # replace spaces outside brackets
    query = re.sub(r'\s(?!([^(\[|\{).]*(\]|\})))', '&', query)
    query = re.sub(r'\s(?!([^(\]|\}).]*(\[|\{)))', '&', query[-1::-1])[-1::-1]

    return query

def _push_nots(expression):
    """"""
    
    # a "pure expression" or leaf
    if expression.is_leaf():
        return expression
    # a CONJ / DISJ expression
    if not expression.operator == NEGOP:
        _push_nots(expression.left)
        _push_nots(expression.right)
        return expression
    # a NOT introducing a leaf 
    if expression.left.is_leaf():
        return expression
    
    # a NOT introduces a subtree
    # in this case apply Third Excluded
    child = expression.left
    if child.operator == NEGOP:
        return child.left
    
    # in this case apply DeMorgan mapping
    expression.operator = {CONOP:DISOP,DISOP:CONOP}[child.operator]
    expression.left  = _push_nots(OperationExpression(NEGOP, child.left))
    expression.right = _push_nots(OperationExpression(NEGOP, child.right))

    return expression
    
def _recognize(query:str):
    """
    extruturamos a arvore, operacoes, roles e IDs
    """
    # * definition, meaning and usability of "compact"
    # * care about the Operators Precedence

    operator = None
    operator_index = None
    # a negation of an expression
    if query.startswith(NEGOP):
        expression = _recognize(query[1:])
        
        # if negation precedes a compact
        if _precedence_neg(expression):
            return OperationExpression(NEGOP, expression)
        
        # searchs first left compact
        parent = expression
        child  = parent.left
        while not _precedence_neg(child):
            parent = child
            child = parent.left
        parent.left = OperationExpression(NEGOP, child)

        return expression

    # expression inside parenthesis
    if query.startswith("("):
        # problem if parenthesis not closed
        closed_parenthesis_index = query.rfind(")")
        if closed_parenthesis_index == -1:
            raise Exception(f"Check parenthesis in {query}")

        # if query simply enclosed by parenthesis
        query_last_index = len(query)-1
        if closed_parenthesis_index == query_last_index:
            expression = _recognize(query[1:closed_parenthesis_index])
            expression.compact = True
            return expression
        
        # defines the operator position
        operator_index = closed_parenthesis_index+1
        operator = query[operator_index]
        left  = _recognize(query[:operator_index])
        right = _recognize(query[operator_index+1:])
        left.compact = True

        return OperationExpression(operator,left,right)
    
    # if not parethesis, finds operators
    operator_index = _find_operator(query, CONOP+DISOP)

    # if not operator, a simple node
    if operator_index == -1:
        return NodeExpression(query)
    
    # both sides if operator
    operator = query[operator_index]
    left  = _recognize(query[:operator_index])
    right = _recognize(query[operator_index+1:])
    
    if operator == DISOP or _precedence_con(right):
        return OperationExpression(operator,left,right)
    parent = right
    child  = parent.left
    while not _precedence_con(child):
        parent = child
        child  = parent.left
    parent.left = OperationExpression(operator, child)

    return OperationExpression(operator,left,right)

def _precedence_neg(expression):
    return expression.is_compact() or expression.operator == NEGOP 

def _precedence_con(expression):
    return _precedence_neg(expression) or expression.operator == CONOP


def _find_operator(query, operators):
    if len(query) == 0 or len(operators) == 0: return -1
    indexes = [query.find(o) for o in operators if o in query]
    return -1 if len(indexes) == 0 else min(indexes)