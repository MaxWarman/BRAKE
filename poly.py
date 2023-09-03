from sympy import Symbol
from sympy.polys.domains import FF

def main():
    x = Symbol('x')
    F = FF(7)
    poly = F(x**3 + x + 1)
    print(poly)

if __name__ == "__main__":
    main()
