
QEQ_BGN = "{"
QEQ_END = "}"

class QEQExpression:
    def __init__(self,expression):
        self.expression = expression
        
        # separates constraints
        self.qeqs = expression.replace(" ","").split(",")
        self.qeqs = [qeq.split("=q") for qeq in self.qeqs]
        # validates the splitting
        for qeq in self.qeqs:
            if not len(qeq) == 2:
                raise Exception(f"Invalid constraint in {expression}")



    def is_leaf(self): return True
    def is_compact(self): return True