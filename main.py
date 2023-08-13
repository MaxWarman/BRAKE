import numpy as np
import numpy.polynomial.polynomial as poly
import sympy

class Group:
    def __init__(self, order):
        self.order = order

class GroupPoly(poly.Polynomial):
    def __init__(self, group: Group, coef: list):
        self.groupOrder = group.order
        super().__init__(coef)
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

def runTests():
    print("\nRunnig tests...")
    G = Group(4)
    assert(GroupPoly(G, [0,1,2,3]) == GroupPoly(G, [4,5,6,7]))
    print("All assertion tests passed!")

def main():
    G = Group(5)
    p1 = GroupPoly(G, [1,2,3,4])
    print(p1)
    print(p1 % 2)

if __name__ == "__main__":
    main()
    runTests()