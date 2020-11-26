PREDICATE = "predicate"

BRACKETS_BGN = "["
BRACKETS_END = "]"
IDENTIFIER_OUT = "[{^"
IDENTIFIER_CHAR = ":"

import re

class NodeExpression():
    def __init__(self,expression):
        """"""
        # * add the QUOTE notation
        # * use Regular Expressions
        # * add _consume_text method?
        # * consider the ALL PATTERNS

        self.expression = expression
        
        self.id = self._trim_id(expression)
        self.roles = self._trim_roles(expression) 

        # Processes the expression between ID and ROLES
        expression = re.sub(".*:", "", expression)
        expression = re.sub("\[.*\]", "", expression)
        self.body = None if len(expression) == 0 else expression
        
        self.values = {PREDICATE:self.body}

    def _trim_id(self,expression):
        """Separates expresion ID if given"""
        # finds identifier
        identifier_end = expression.find(IDENTIFIER_CHAR)
        if identifier_end == -1:
            return None
        identifier = expression[:identifier_end]

        # validates identifier
        for char in IDENTIFIER_OUT:
            if char in identifier:
                raise Exception(f"Check identifiers in {expression}")

        return identifier

    def _trim_roles(self,expression):
        """Separates the roles from expression"""
        # * add the QUOTE notation
        # * why using a CLASS for ROLE?
        # * add expception for ROLE
        # * use Regular Expressions

        # if there are no ROLES
        if len(expression) <= 3 or not expression.endswith(BRACKETS_END):
            return None
        
        # search for ROLES
        end = expression.rfind(BRACKETS_END)
        bgn = expression.rfind(BRACKETS_BGN)

        if bgn == -1:
            raise Exception(f"Invalid expression {expression}")

        roles = expression[bgn+1:end]
        roles_ = []
        for role in roles.split(","):
            splitted = role.strip().split(" ")
            if not len(splitted) == 2:
                raise Exception(f"Check ROLES in {expression}")
            roles_.append(splitted)
        
        return roles_

    def is_leaf(self): return True
    def is_compact(self): return True