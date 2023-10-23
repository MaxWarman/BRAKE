"""
What happens in enrolment:
- picking group order
- input: enrolment template
- establishing verification threshold
"""

import random
import hashlib
import json

from group_poly import Group
from fuzzy_vault import FuzzyVault
from rsa import generate_key


class Client:

    @classmethod
    def enrol(cls, client_id: int, enrolment_template: list, verify_threshold: int, DEBUG=False):
        G = Group(prime=12401)
        secret_polynomial = FuzzyVault.generate_secret_polynomial(group_order=G.order, sec_poly_deg=verify_threshold)

        fuzzy_vault = FuzzyVault(group_order=G.order, bio_template=enrolment_template, secret_polynomial=secret_polynomial, verify_threshold=verify_threshold, DEBUG=DEBUG)
        
        r, r_inv, r_mod = cls.generate_blinding_exponent()
        # print(f"r: {r}")
        # print(f"r_inv: {r_inv}")
        # print(f"r_mod: {r_mod}\n")

        assert((r * r_inv)%r_mod == 1)

        # Blind secret polynomial
        blinded_polynomial = cls.blind(secret_polynomial, r, r_mod)

        # Send 'blinded_polynomial' to Evaluator
        # TODO - change 'evaluated_polynomial' to be equal to value returned by the Evaluator
        evaluated_polynomial = blinded_polynomial

        # Unblind result returned by the Evaluator
        r_inv = -r % r_mod
        unblinded_evaluator_result = cls.unblind(evaluated_polynomial, r_inv, r_mod)

        # Generate client key pair
        client_private_key = generate_key(unblinded_evaluator_result)
        client_private_key_PEM = client_private_key.exportKey("PEM")
        client_public_key_PEM = client_private_key.publickey().exportKey("PEM")

        # Send (id, V(x), cpk_t) to the server
        public_values_json = Client.get_public_values_json(client_id, fuzzy_vault.vault_polynomial.coef.tolist(), str(client_public_key_PEM), G.order)
        
        return public_values_json

    @classmethod
    def blind(cls, secret_polynomial, r, r_mod):
        txt = ""
        for i, coef in enumerate(secret_polynomial.coef):
            txt += str(coef)
            if i < len(secret_polynomial.coef) - 1:
                txt += ","

        hashed_polynomial = hashlib.sha256(txt.encode("utf-8")).hexdigest()
        hashed_polynomial_int = int(hashed_polynomial, 16)
        
        #blind = pow(hashed_polynomial_int, r, r_mod)
        blind = (hashed_polynomial_int + r) % r_mod
        blind = hex(blind)[2:]

        return blind


    @classmethod
    def unblind(cls, evaluated_polynomial, r_inv, r_mod):
        evluated_polynomial_int = int(evaluated_polynomial, 16)
        
        #unblind = pow(evaluated_polynomial_int, r_inv, r_mod)
        unblind = (evluated_polynomial_int + r_inv) % r_mod
        unblind = hex(unblind)[2:]

        return unblind

    @classmethod
    def generate_blinding_exponent(cls):
        r_bottom_boundry = 2
        r_top_boundry = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff42
        r_mod = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff43

        found_r_inv = False
        while not found_r_inv:
            r = random.randint(r_bottom_boundry, r_top_boundry)
            try:
                r_inv = pow(r, -1, r_mod)
                found_r_inv = True
            except:
                continue
        
        return (r, r_inv, r_mod)
    
    @classmethod
    def get_public_values_json(cls, client_id: int, vault_coefs: list, client_public_key_PEM: str, group_order: int):

        public_values_dict = {
            "client_id": client_id,
            "vault_coefs": list(vault_coefs),
            "client_public_key_PEM": client_public_key_PEM,
            "group_order": group_order,
        }

        return json.dumps(public_values_dict)

def run_tests():
    enrol_bottom_boundry = 1
    enrol_up_boundry = 8

    enrol_template = [1,2,3,4,5,6,7,8] + [random.randint(enrol_bottom_boundry, enrol_up_boundry) for i in range(36)]

    id = 1

    public_values_json = Client.enrol(client_id=id, enrolment_template=enrol_template, verify_threshold=8)

    print(public_values_json)

def main():
    run_tests()

if __name__ == "__main__":
    main()


"""
TODO:


"""