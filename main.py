import sympy
import numpy as np

class Group:
    def __init__(self, order):
        self.order = order

class GroupPoly():
    def __init__(self, group_order: int, coef: list):
            self.group_order = group_order
            self.coef = np.array(coef, dtype=int)
            self.update_poly()

    def mod_poly(self):
        self.coef %= self.group_order

    def reduce_poly(self):
        i = len(self.coef) - 1
        while i > 0:
            if self.coef[i] != 0:
                return
            self.coef = np.delete(self.coef, -1)
            i -= 1

    def update_poly(self):
        self.mod_poly()
        self.reduce_poly()

    def degree(self):
        for i, c in enumerate(self.coef[::-1]):
            if c != 0:
                return len(self.coef) - i - 1
        return 0

    def __str__(self):
        txt  = f"f[x] = "
        l = len(self.coef)
        for i,c in enumerate(self.coef):
            txt += f"{c} "
            if i != 0:
                txt += f"x**{i} "
            if i != l - 1:
                txt += "+ "
        txt += f", "        
        txt += f"deg(f) = {self.degree()}, "
        txt += f"|G| = {self.group_order}"
        return txt

    def _add(self, other_poly):
        if self.group_order != other_poly.group_order:
            raise ValueError("Polynomials must have the same group order!")

        # Pad coefficient arrays with zeros to have the same length 
        max_len = max(len(self.coef), len(other_poly.coef))
        coef1 = np.pad(self.coef, (0, max_len - len(self.coef)))
        coef2 = np.pad(other_poly.coef, (0, max_len - len(other_poly.coef)))

        # Add coefficients and modulo reduce result by group order
        result_coef = (coef1 + coef2) % self.group_order

        return result_coef
    
    def _subtract(self, other_poly):
        if self.group_order != other_poly.group_order:
            raise ValueError("Polynomials must have the same group order!")
        
        # Pad coefficient arrays with zeros to have the same length 
        max_len = max(len(self.coef), len(other_poly.coef))
        coef1 = np.pad(self.coef, (0, max_len - len(self.coef)))
        coef2 = np.pad(other_poly.coef, (0, max_len - len(other_poly.coef)))

        # Subtract coefficients and modulo reduce result by group order
        result_coef = (coef1 - coef2) % self.group_order

        return result_coef
    
    def _multiply(self, other_poly):
        if self.group_order != other_poly.group_order:
            raise ValueError("Polynomials must have the same group order!")
        
        # Calculate degree of resulting polynomial
        degree1 = self.degree()
        degree2 = other_poly.degree()
        result_degree = degree1 + degree2

        # Initialize the result coefficient array with zeros
        result_coef = np.zeros(result_degree + 1, dtype=int)

        # Perform coefficient-wise multiplication and addition
        for i, coef1 in enumerate(self.coef):
            for j, coef2 in enumerate(other_poly.coef):
                result_coef[i+j] += coef1 * coef2
        # Modulo reduction
        result_coef %= self.group_order

        return result_coef

    def __add__(self, other_poly):
        try:
            result_coef = self._add(other_poly)
        except Exception as err:
            raise err

        return GroupPoly(self.group_order, result_coef)
    
    def __sub__(self, other_poly):
        try:
            result_coef = self._subtract(other_poly)
        except Exception as err:
            raise err

        return GroupPoly(self.group_order, result_coef)
    
    def __mul__(self, other_poly):
        try:
            result_coef = self._multiply(other_poly)
        except Exception as err:
            raise err
        
        return GroupPoly(self.group_order, result_coef)

def runTests():
    print("\nRunnig tests...")
    G = Group(4)
    assert(GroupPoly(G.order, [0,1,2,3]) == GroupPoly(G.order, [4,5,6,7]))
    print("All assertion tests passed!")

def main():
    G = Group(7)
    p1 = GroupPoly(G.order, [1,1])
    p2 = GroupPoly(G.order, [1,1])
    print(p1)
    print(p2)

    print(p1*p2)
    print(p1-p2)

if __name__ == "__main__":
    main()
    # runTests()

"""
To do:

"""