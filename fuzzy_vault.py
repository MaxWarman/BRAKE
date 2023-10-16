import secrets
import random
import galois
import numpy as np
from group_poly import Group, GroupPoly

class FuzzyVault:

    def __init__(self, group_order: int, bio_template: list, verify_threshold: int):
        self.bio_template = bio_template
        self.bio_template_length = len(self.bio_template)
        self.verify_threshold = verify_threshold
        
        self.vault_polynomial = self.lock(group_order, self.bio_template, self.verify_threshold)

    def __str__(self):
        txt = "Fuzzy Vault:\n"
        txt += f"Biometrics template length: {self.bio_template_length}\n"
        txt += f"Verification threshold tau: {self.verify_threshold}\n"
        txt += f"Vault: {str(self.vault_polynomial)}\n"
        return txt

    @classmethod
    def generate_secret_polynomial(cls, group_order, sec_poly_deg):
        secret_coefs = np.array([], dtype=np.uint64)
        for i in range(sec_poly_deg):
            upper_bound = group_order - 1
            lower_bound = 0 if i != sec_poly_deg - 1 else 1

            rand_coef = int(secrets.randbelow(upper_bound - lower_bound + 1) + lower_bound)
            secret_coefs = np.append(secret_coefs, rand_coef)

        return GroupPoly(group_order, secret_coefs)

    @classmethod
    def lock(cls, group_order, bio_template, verify_threshold):
        vault_polynomial = GroupPoly.one(group_order)
        for value in bio_template:
            multiplication_component = GroupPoly(group_order, [-value, 1])
            vault_polynomial = vault_polynomial * multiplication_component
        secret_polynomial = cls.generate_secret_polynomial(group_order, verify_threshold)
        print(f"secret polynomial: {secret_polynomial}")
        vault_polynomial = vault_polynomial + secret_polynomial
        return vault_polynomial

    @classmethod
    def unlock(cls, fuzzy_vault,  group_order, bio_template):

        GF = galois.GF(group_order)
        x = GF(bio_template)
        y = [fuzzy_vault.vault_polynomial.eval(arg) for arg in bio_template]
        y = GF(y)

        interpolated_polynomial = galois.lagrange_poly(x, y)
        secret_polynomial_coeffs = np.array([int(coefficient) for coefficient in interpolated_polynomial.coefficients()[::-1]])
        secret_polynomial = GroupPoly( group_order=group_order, coef=secret_polynomial_coeffs)

        return secret_polynomial

def main():
    G = Group(prime=12401)
    enroll_template = [random.randint(0,15) for i in range(44)]
    fv = FuzzyVault(group_order=G.order, bio_template=enroll_template, verify_threshold=6)
    print(fv)
    a = FuzzyVault.unlock(fv, group_order=G.order, bio_template=[1,2,3,4,5,6])
    print(a)

if __name__ == "__main__":
    main()

"""
TODO:
- works for exactly the same bio_templates BUT:
    - cannot have more than one of the same vlaue as x 

Important docs - Galois module:
https://mhostetter.github.io/galois/latest/api/galois.FieldArray/#examples
https://stackoverflow.com/questions/48065360/interpolate-polynomial-over-a-finite-field
https://pypi.org/project/galois/
https://github.com/mhostetter/galois
"""