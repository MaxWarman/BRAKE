import sympy
import numpy as np


class Group:
    def __init__(self, prime: int):
        """
        Group class constructor that returns Group instantiation object.

        Parameters:
            - prime (int): Prime number that will be treated as group order.

        Returns:
            - self (Group): Group class object
        """

        # Test if given group order is prime number
        if not sympy.isprime(prime):
            raise ValueError(f"Given group order is not prime: p = {prime}")
        self.order = prime


class GroupPoly:
    def __init__(self, group_order: int, coef: list):
        """
        GroupPoly class constructor that returns GroupPoly instantination object

        Parameters:
            - group_order (int): Prime order of group that the polynomial is put in
            - coef (list): Coefficients of polynomial with coefficients of lowest powers put in the lowest indices of the list

        Returns:
            - self (GroupPoly): GroupPoly class object
        """
        self.group_order = group_order
        self.coef = np.array(coef, dtype=object)
        self.update_poly()

    def mod_poly(self) -> None:
        """
        Set values of all polynomial's coefficients to their value modulo group order of the polynomial

        Parameters:
            - None

        Returns:
            - None
        """
        self.coef %= self.group_order

    def reduce_poly(self) -> None:
        """
        Reduce polynomial by popping leading zeros in the coefficient list

        Parameters:
            - None

        Returns:
            - None
        """
        i = len(self.coef) - 1
        while i > 0:
            if self.coef[i] != 0:
                return
            self.coef = np.delete(self.coef, -1)
            i -= 1

    def update_poly(self) -> None:
        """
        Perform mod_poly() and reduce_poly() operations on polynomial

        Parameters:
            - None

        Returns:
            - None
        """
        self.mod_poly()
        self.reduce_poly()

    def degree(self) -> int:
        """
        Return degree of polynomial

        Parameters:
            - None

        Returns:
            degree (int): Degree of given polynomial
        """
        for i, c in enumerate(self.coef[::-1]):
            if c != 0:
                return len(self.coef) - i - 1
        return 0

    def eval(self, arg: int) -> int:
        """
        Evaluate polynomial value f[x] for certain input value x

        Parameters:
            - arg (int): Function argument 'x' to calculate value of polynomial at

        Returns:
            - value (int): Value f(x) of given polynomial
        """
        value = 0
        for i, coef in enumerate(self.coef):
            value += (coef * pow(arg, i, self.group_order)) % self.group_order
        value %= self.group_order
        return int(value)

    def __str__(self):
        txt = f"f[x] = "
        l = len(self.coef)
        for i, c in enumerate(self.coef):
            txt += f"{c}"
            if i != 0:
                txt += " "
                txt += f"x^{i}"
            if i != l - 1:
                txt += " + "
        txt += f", "
        txt += f"deg(f) = {self.degree()}, "
        txt += f"|G| = {self.group_order}"
        return txt

    def _add(self, other_poly):
        if not isinstance(other_poly, GroupPoly):
            raise ValueError("Objects both must be of class GroupPoly!")

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
        if not isinstance(other_poly, GroupPoly):
            raise ValueError("Objects both must be of class GroupPoly!")

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
        if not isinstance(other_poly, GroupPoly):
            raise ValueError("Objects both must be of class GroupPoly!")

        if self.group_order != other_poly.group_order:
            raise ValueError("Polynomials must have the same group order!")

        # Calculate degree of resulting polynomial
        degree1 = self.degree()
        degree2 = other_poly.degree()
        result_degree = degree1 + degree2

        # Initialize the result coefficient array with zeros
        result_coef = np.zeros(result_degree + 1, dtype=object)

        # Perform coefficient-wise multiplication and addition
        for i, coef1 in enumerate(self.coef):
            for j, coef2 in enumerate(other_poly.coef):
                result_coef[i + j] += (coef1 * coef2) % self.group_order

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

    def __neg__(self):
        result_coef = np.array(self.coef, dtype=object)
        result_coef *= -1

        return GroupPoly(self.group_order, result_coef)

    def __eq__(self, other_poly):
        if not isinstance(other_poly, GroupPoly):
            print("GroupPoly.__eq__(): Objects both must be of class GroupPoly!")
            return False

        if self.group_order != other_poly.group_order:
            raise ValueError("Polynomials must have the same group order!")

        # Pad coefficient arrays with zeros to have the same length
        max_len = max(len(self.coef), len(other_poly.coef))
        coef1 = np.pad(self.coef, (0, max_len - len(self.coef)))
        coef2 = np.pad(other_poly.coef, (0, max_len - len(other_poly.coef)))

        for i in range(len(coef1)):
            if coef1[i] != coef2[i]:
                return False
        return True

    @classmethod
    def zero(cls, group_order: int):
        return cls(group_order, [0])

    @classmethod
    def one(cls, group_order: int):
        return cls(group_order, [1])


def run_tests():
    print("Running tests...")

    # Tests for Group of order 7
    G = Group(prime=7)
    group_order = G.order

    # Test polynomials
    poly1 = GroupPoly(group_order, [3, 2, 13])  # 3 + 2x + 13x^2 mod 7
    poly2 = GroupPoly(group_order, [4, 7, 1])  # 4 + x^2 mod 7

    # Addidion test
    assert (poly1 + poly2) == GroupPoly(group_order, [0, 2])
    assert (poly1 + GroupPoly.zero(group_order)) == poly1

    # Subtraction test
    assert (poly1 - poly2) == GroupPoly(group_order, [6, 2, 5])
    assert (poly1 - GroupPoly.zero(group_order)) == poly1

    # Multiplication test
    assert (poly1 * poly2) == GroupPoly(group_order, [5, 1, 6, 2, 6])
    assert (poly1 * GroupPoly.one(group_order)) == poly1

    # Negation test
    assert -poly1 == GroupPoly(group_order, [4, 5, 1])
    assert -GroupPoly.zero(group_order) == GroupPoly.zero(group_order)
    assert -GroupPoly.one(group_order) == GroupPoly(group_order, [group_order - 1])

    # Zero polynomial test
    assert GroupPoly.zero(group_order) == GroupPoly(group_order, [0])

    # One polynomial test
    assert GroupPoly.one(group_order) == GroupPoly(group_order, [1])

    print("Tests completed!")


def main():
    run_tests()


if __name__ == "__main__":
    main()
