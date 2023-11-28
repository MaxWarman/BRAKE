import secrets
import random
import galois
import numpy as np
from group_poly import Group, GroupPoly

class FuzzyVault:

    def __init__(self, group_order: int, bio_template: list):#, secret_polynomial: list, verify_threshold: int, DEBUG=False):
        """
        param group_order: order of a group to use for finite field calculations;
        param bio_template: enrolment biometrics template;
        param secret_polynomial: secret polynomial to use during enrolment phase
        param verify_threshold: value of tau - how many biometrics parameters have to match with enrolment template at least
        param DEBUG: if set to True, additional description will be logged
        """
        
        self.group_order = group_order
        self.bio_template = bio_template
        self.bio_template_length = len(self.bio_template)

    def __str__(self):
        txt = "Fuzzy Vault:\n"
        txt += f"Biometrics template length: {self.bio_template_length}\n"
        txt += f"Vault: {str(self.vault_polynomial)}\n"
        return txt

    @classmethod
    def generate_secret_polynomial(cls, group_order: int, sec_poly_deg: int) -> GroupPoly:
        secret_coefs = np.array([], dtype=np.uint64)
        for i in range(sec_poly_deg):
            upper_bound = group_order - 1
            lower_bound = 0 if i != sec_poly_deg - 1 else 1

            rand_coef = int(secrets.randbelow(upper_bound - lower_bound + 1) + lower_bound)
            secret_coefs = np.append(secret_coefs, rand_coef)

        return GroupPoly(group_order, secret_coefs)

    def lock(self, secret_polynomial=None) -> None:
        vault_polynomial = GroupPoly.one(self.group_order)
        for value in self.bio_template:
            multiplication_component = GroupPoly(self.group_order, [-value, 1])
            vault_polynomial = vault_polynomial * multiplication_component
        vault_polynomial = vault_polynomial + secret_polynomial
        self.vault_polynomial = vault_polynomial

    def get_random_arguments(self, how_many_indices: int):
        set_of_indices = set(range(self.bio_template_length))
        random_indices_of_bio_set = sorted(random.sample(set_of_indices, how_many_indices))
        random_arguments = [self.bio_template[ind] for ind in random_indices_of_bio_set]
        return random_arguments

    def unlock(self, verify_threshold: int) -> GroupPoly:
        GF = galois.GF(self.group_order)
        number_of_unlocking_rounds = 3000

        poly_counting_dict = {}
        for i in range(number_of_unlocking_rounds):
            arguments = GF(self.get_random_arguments(verify_threshold))
            values = [self.vault_polynomial.eval(int(arg)) for arg in arguments]
            values = GF(values)

            try:
                interpolated_polynomial = galois.lagrange_poly(arguments, values)
            except:
                continue
            
            secret_polynomial_coeffs = list([int(coefficient) for coefficient in interpolated_polynomial.coefficients()[::-1]])
            if str(secret_polynomial_coeffs) not in poly_counting_dict.keys():
                poly_counting_dict[str(secret_polynomial_coeffs)] = 1
            else:
                poly_counting_dict[str(secret_polynomial_coeffs)] += 1

        most_common_coefs_str = str(max(poly_counting_dict, key=poly_counting_dict.get))
        secret_polynomial_coeffs = [int(val) for val in most_common_coefs_str.replace("[", "").replace("]", "").split(", ")]
        secret_polynomial = GroupPoly( group_order=self.group_order, coef=secret_polynomial_coeffs)

        return secret_polynomial
    
    def set_vault_polynomial(self, vault_polynomial_coefs: list) -> None:
        self.vault_polynomial = GroupPoly(group_order=self.group_order, coef=vault_polynomial_coefs)

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
    retrieved_secret_polynomial = FuzzyVault.unlock(fv, group_order=G.order, bio_template=verification_template)
    
    if DEBUG:
        print(fv)
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