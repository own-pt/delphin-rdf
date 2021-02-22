class TempData:
    def __init__(self):
        """"""
        self.count = 99
        self.variables = []
    
    def new_variable(self):
        """"""
        self.count = self.count + 1
        variable = f"aux{self.count}"

        return variable
