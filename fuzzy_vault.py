import secrets
import numpy as np
from group_poly import Group, GroupPoly

class FuzzyVault:

    def __init__(self, group_order: int, bio_template: list, verify_threshold: int, sec_parameter: int):
        self.bio_template = bio_template
        self.bio_template_length = len(self.bio_template)
        self.verify_threshold = verify_threshold
        self.sec_parameter = sec_parameter
        
        self.vault = self.lock(group_order, self.bio_template, self.sec_parameter)

    def __str__(self):
        txt = "Fuzzy Vault:\n"
        txt += f"Biometrics template length: {self.bio_template_length}\n"
        txt += f"Verification threshold tau: {self.verify_threshold}\n"
        txt += f"Security parameter lambda: {self.sec_parameter}\n"
        txt += f"Vault: {str(self.vault)}\n"
        return txt

    @classmethod
    def generate_secret_polynomial(cls, group_order, sec_parameter):
        secret_coefs = np.array([])
        for i in range(sec_parameter):

            upper_bound = group_order - 1
            lower_bound = 0 if i != sec_parameter - 1 else 1

            rand_coef = secrets.randbelow(upper_bound - lower_bound + 1) + lower_bound
            np.append(secret_coefs, rand_coef)

        return GroupPoly(group_order, secret_coefs)

    @classmethod
    def lock(cls, group_order, bio_template, sec_parameter):
        vault = GroupPoly.one(group_order)
        for value in bio_template:
            multiplication_component = GroupPoly(group_order, [-value, 1])
            vault = vault * multiplication_component

        secret_polynomial = cls.generate_secret_polynomial(group_order, sec_parameter)
        vault = vault + secret_polynomial
        return vault

def main():
    G = Group(7)
    fv = FuzzyVault(G.order, [1,1], 7, 2)
    print(fv)

if __name__ == "__main__":
    main()