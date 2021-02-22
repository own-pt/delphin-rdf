
OPERATOR_AND = OPERATOR_CON = "&"
OPERATOR_NOT = OPERATOR_NEG = "!"
OPERATOR_ORR = OPERATOR_DIS = "|"
OPERATOR_ALL = OPERATOR_ANY = OPERATOR_CON+OPERATOR_DIS+OPERATOR_NEG

class OperationExpression():
    def __init__(self,operation,left,right=None):
        self.left = left
        self.operator = operation
        self.right = left if right == None else right

        self.compact = False
    
    def is_leaf(self): return False
    def is_compact(self): return self.compact