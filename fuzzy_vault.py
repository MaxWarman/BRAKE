import secrets
import random
import galois
import numpy as np
from group_poly import Group, GroupPoly

class FuzzyVault:

    def __init__(self, group_order: int, bio_template: list, secret_polynomial: list, verify_threshold: int, DEBUG=False):
        """
        param group_order: order of a group to use for finite field calculations;
        param bio_template: enrolment biometrics template;
        param secret_polynomial: secret polynomial to use during enrolment phase
        param verify_threshold: value of tau - how many biometrics parameters have to match with enrolment template at least
        param DEBUG: if set to True, additional description will be logged
        """
        
        self.bio_template = bio_template
        self.bio_template_length = len(self.bio_template)
        self.verify_threshold = verify_threshold
        self.group_order = group_order

        self.secret_polynomial = secret_polynomial
        self.vault_polynomial = self.lock(group_order=self.group_order, bio_template=self.bio_template, secret_polynomial=secret_polynomial, DEBUG=DEBUG)

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
    def lock(cls, group_order, bio_template, secret_polynomial=None, DEBUG=False):
        vault_polynomial = GroupPoly.one(group_order)
        for value in bio_template:
            multiplication_component = GroupPoly(group_order, [-value, 1])
            vault_polynomial = vault_polynomial * multiplication_component
        if DEBUG:
            print(f"Enrolment secret polynomial: {secret_polynomial}")
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

def run_tests():
    print("Running fuzzy_vault.py tests...")
    DEBUG = True

    G = Group(prime=12401)
    enrol_bottom_boundry = 0
    enrol_top_boundry = 8

    enrol_template = [1,2,3,4,5,6,7,8] + [random.randint(enrol_bottom_boundry, enrol_top_boundry) for i in range(36)]
    verification_template = [1,2,3,4,5,6,7,8]
    verify_threshold = len(verification_template)
    secret_polynomial = FuzzyVault.generate_secret_polynomial(group_order=G.order, sec_poly_deg=verify_threshold)

    fv = FuzzyVault(group_order=G.order, bio_template=enrol_template, secret_polynomial=secret_polynomial, verify_threshold=verify_threshold, DEBUG=DEBUG)
    if DEBUG:
        print(fv)
    retrieved_secret_polynomial = FuzzyVault.unlock(fv, group_order=G.order, bio_template=verification_template)
    
    print(f"Retrieved secret polynomial: {retrieved_secret_polynomial}")

    assert(secret_polynomial == retrieved_secret_polynomial)

    print("\nTests completed!")

def main():
    run_tests()

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