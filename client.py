"""
What happens in enrolment:
- picking group order
- input: enrolment template
- establishing verification threshold
"""

import random
import hashlib
from sympy import nextprime
from group_poly import Group
from fuzzy_vault import FuzzyVault

class Client:

    @classmethod
    def enrol(cls, enrolment_template: list, verify_threshold: int, DEBUG=False):
        G = Group(prime=12401)
        secret_polynomial = FuzzyVault.generate_secret_polynomial(group_order=G.order, sec_poly_deg=verify_threshold)

        fuzzy_vault = FuzzyVault(group_order=G.order, bio_template=enrolment_template, secret_polynomial=secret_polynomial, verify_threshold=verify_threshold, DEBUG=DEBUG)
        
        # Evaluate 'f' with the evaluator
        blinded_polynomial = cls.blind(secret_polynomial=secret_polynomial)
        # Send (id, V, cpk_t) to the server
    
    @classmethod
    def blind(cls, secret_polynomial):
        r, r_inv, r_mod = cls.generate_binding_exponent()

        txt = ""
        for i, coef in enumerate(secret_polynomial.coef):
            txt += str(coef)
            if i < len(secret_polynomial.coef) - 1:
                txt += ","


        hashed_polynomial = hashlib.sha256(txt.encode("utf-8")).hexdigest()

        hashed_polynomial_int = int(hashed_polynomial, 16)
        blind = pow(hashed_polynomial_int, r, r_mod)
        blind = hex(blind)[2:]


        blind_int = int(blind, 16)
        unblind = pow(blind_int, r_inv, r_mod)

        unblind = hex(unblind)[2:]

        print(f"hashed_polynomial: {hashed_polynomial}")
        print(f"blind: {blind}")
        print(f"unblind: {unblind}")

        # hashed_polynomial_int = int(hashed_polynomial, 16)
        # poly_to_r = pow(hashed_polynomial_int, r, r_mod)
        # poly_to_minus_r = pow(poly_to_r, r_inv, r_mod)
        # print(hex(poly_to_minus_r)[2:]) 

        # evaluated_value_dec = pow(input_value_dec, self.secret_key, self.mod)
        # evaluated_value_hex = hex(evaluated_value_dec)[2:]


        # print(blinded_polynomial)

        return 1
    
    @classmethod
    def generate_binding_exponent(cls):
        r_bottom_boundry = 2
        r_top_boundry = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff 
        r_mod = 0x10000000000000000000000000000000000000000000000000000000000000000

        found_r_inv = False
        while not found_r_inv:
            r = random.randint(r_bottom_boundry, r_top_boundry)
            try:
                r_inv = pow(r, -1, r_mod)
                found_r_inv = True
            except:
                continue
        
        return (r, r_inv, r_mod)

def power(a,b,m):
    result = 1
    for i in range(b):
        result *= a
        result %= m
    return result

def run_tests():
    enrol_bottom_boundry = 1
    enrol_up_boundry = 8

    enrol_template = [1,2,3,4,5,6,7,8] + [random.randint(enrol_bottom_boundry, enrol_up_boundry) for i in range(36)]
    Client.enrol(enrolment_template=enrol_template, verify_threshold=8)

def main():
    run_tests()

if __name__ == "__main__":
    main()


"""
TODO:
- why pow() returns '0'
    - probably because H(f) has to be generator of Z_q in the end
"""