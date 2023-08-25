import numpy as np
import numpy.polynomial.polynomial as poly
import sympy

class Group:
    def __init__(self, order):
        self.order = order

class GroupPoly(poly.Polynomial):
    def __init__(self, groupOrder: int, coef: list, domain=None, window=None, symbol='x'):
        self.groupOrder = groupOrder
        super().__init__(coef, domain, window, symbol)
        self.updatePoly()

    def modPoly(self):
        for i, c in enumerate(self.coef):
            self.coef[i] = c % self.groupOrder

    def reducePoly(self):
        i = len(self.coef) - 1
        while self.coef[-1] == 0 and i != 0 :
            self.coef = np.delete(self.coef, -1)
            i -= 1

    def updatePoly(self):
        self.modPoly()
        self.reducePoly()

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
        txt += f"|G| = {self.groupOrder}"
        return txt

    def __add__(self, other):
        if self.groupOrder != other.groupOrder:
            raise ValueError("Polynomials must have the same group order!")
        try:
            resultCoef = self._add(self.coef, other.coef)
        except Exception as e:
            raise e
        return GroupPoly(self.groupOrder, resultCoef)

def runTests():
    print("\nRunnig tests...")
    G = Group(4)
    assert(GroupPoly(G.order, [0,1,2,3]) == GroupPoly(G.order, [4,5,6,7]))
    print("All assertion tests passed!")

def main():
    G = Group(5)
    p1 = GroupPoly(G.order, [1,2,3,4])
    p2 = GroupPoly(G.order, [1,2,3,4])

    print(p1)

if __name__ == "__main__":
    main()
    # runTests()

"""
To do:
- fix operations like addition/multiplication
"""