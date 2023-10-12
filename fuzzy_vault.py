import secrets
import galois
import numpy as np
from group_poly import Group, GroupPoly

class FuzzyVault:

    def __init__(self, group_order: int, bio_template: list, verify_threshold: int, sec_parameter: int):
        self.bio_template = bio_template
        self.bio_template_length = len(self.bio_template)
        self.verify_threshold = verify_threshold
        self.sec_parameter = sec_parameter
        
        self.vault = self.lock(group_order, self.bio_template, self.verify_threshold)

    def __str__(self):
        txt = "Fuzzy Vault:\n"
        txt += f"Biometrics template length: {self.bio_template_length}\n"
        txt += f"Verification threshold tau: {self.verify_threshold}\n"
        txt += f"Security parameter lambda: {self.sec_parameter}\n"
        txt += f"Vault: {str(self.vault)}\n"
        return txt

    @classmethod
    def generate_secret_polynomial(cls, group_order, sec_poly_deg):
        secret_coefs = np.array([], dtype=np.uint64)
        for i in range(sec_poly_deg):
            upper_bound = group_order - 1
            lower_bound = 0 if i != sec_poly_deg - 1 else 1

            rand_coef = np.uint64(secrets.randbelow(upper_bound - lower_bound + 1) + lower_bound)
            secret_coefs = np.append(secret_coefs, rand_coef)

        return GroupPoly(group_order, secret_coefs)

    @classmethod
    def lock(cls, group_order, bio_template, verify_threshold):
        vault = GroupPoly.one(group_order)
        for value in bio_template:
            multiplication_component = GroupPoly(group_order, [-value, 1])
            vault = vault * multiplication_component

        secret_polynomial = cls.generate_secret_polynomial(group_order, verify_threshold)
        print(f"secret polynomial: {secret_polynomial}")
        vault = vault + secret_polynomial
        return vault

    @classmethod
    def unlock(cls, fuzzy_vault,  group_order, bio_template, sec_parameter):

        GF = galois.GF(group_order)
        print(GF.properties)
        x = GF(bio_template)
        print(f"x {type(x)}: {x}")
        y = [fuzzy_vault.vault.eval(arg) for arg in bio_template]
        y = GF(y)
        print(f"y {type(y)}: {y}")

        f = galois.lagrange_poly(x, y)
        
        print(f)

        return None

def main():
    G = Group(2137)
    fv = FuzzyVault(group_order=G.order, bio_template=[1,2,3,4,5,8], verify_threshold=4, sec_parameter=2)

    print(fv)

    a = FuzzyVault.unlock(fv, group_order=G.order, bio_template=[1,2,3,4,5,8], sec_parameter=2)
    
if __name__ == "__main__":
    main()

"""
TODO:
- works for exactly the same bio_templates BUT:
    - cannot have more than one of the same vlaue as x
- we do not use all of values in bio template to create fuzzy_vault (specify how many - the same amount as we want to verify?)
- does not work for very large GF orders - even over 2**16 - ints are to small? 

Important docs - Galois module:
https://mhostetter.github.io/galois/latest/api/galois.FieldArray/#examples
https://stackoverflow.com/questions/48065360/interpolate-polynomial-over-a-finite-field
https://pypi.org/project/galois/
https://github.com/mhostetter/galois
"""