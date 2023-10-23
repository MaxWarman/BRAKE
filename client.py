import random
import hashlib
import json
import numpy as np

from group_poly import Group
from fuzzy_vault import FuzzyVault
from evaluator import Evaluator
from rsa import generate_key


class Client:

    def __init__(self, client_id: int, biometrics_template: list):
        self.id = client_id
        self.biometrics_template = biometrics_template

    def enrol(self, verify_threshold: int, G: Group, DEBUG=False):
        # Generate secret polynomial for the Client with given ID
        secret_polynomial = FuzzyVault.generate_secret_polynomial(group_order=G.order, sec_poly_deg=verify_threshold)

############### DELETE
        secret_polynomial.coef = np.array([1] * len(secret_polynomial.coef))

        # Create FuzzyVault using secret polynomial and lock it
        fuzzy_vault = FuzzyVault(group_order=G.order, bio_template=self.biometrics_template, secret_polynomial=secret_polynomial, verify_threshold=verify_threshold, DEBUG=DEBUG)

        # Gennerate blinding exponent and its multiplicative inverse
        r, r_inv, r_mod = Client.generate_blinding_exponent()
        assert((r * r_inv)%r_mod == 1)

        # Blind secret polynomial
        print(f"secret poly: {secret_polynomial}")
        blinded_polynomial = Client.blind(secret_polynomial, r, r_mod)
        print(f"blinded poly: {blinded_polynomial}")
        
        # Evaluate blinded polynomial with Evaluator 
        evaluator = Evaluator()
        evaluated_polynomial = evaluator.evaluate(blinded_polynomial)
        print(f"evaluated poly: {evaluated_polynomial}")

        # Unblind result returned by the Evaluator
        # r_inv = -r % r_mod
        r_inv = G.order - 1 - r
        unblinded_evaluator_result = Client.unblind(evaluated_polynomial, r_inv, r_mod)
        print(f"unblinded poly: {unblinded_evaluator_result}")

        # Generate seeded client key pair
        client_private_key = generate_key(unblinded_evaluator_result)
        client_public_key_PEM = client_private_key.publickey().exportKey("PEM")
        client_public_key_PEM = client_public_key_PEM.decode("utf-8")

        # Send (id, V(x), cpk_t) to the server
        public_values_json = Client.get_public_values_json(self.id, fuzzy_vault.vault_polynomial.coef.tolist(), client_public_key_PEM, G.order, verify_threshold)
        
        return public_values_json
    
    def verify(self):
        NotImplemented

    @classmethod
    def blind(cls, secret_polynomial, r, r_mod):
        txt = ""
        for i, coef in enumerate(secret_polynomial.coef):
            txt += str(coef)
            if i < len(secret_polynomial.coef) - 1:
                txt += ","

        hashed_polynomial = hashlib.sha256(txt.encode("utf-8")).hexdigest()
        print(f"blind(): hashed poly: {hashed_polynomial}")
        hashed_polynomial_int = int(hashed_polynomial, 16)
        
        #blind = pow(hashed_polynomial_int, r, r_mod)
        blind = (hashed_polynomial_int + r) % r_mod
        blind = hex(blind)[2:]

        return blind


    @classmethod
    def unblind(cls, evaluated_polynomial, r_inv, r_mod):
        evaluated_polynomial_int = int(evaluated_polynomial, 16)
        
        #unblind = pow(evaluated_polynomial_int, r_inv, r_mod)
        unblind = (evaluated_polynomial_int + r_inv) % r_mod
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
    def get_public_values_json(cls, client_id: int, vault_coefs: list, client_public_key_PEM: str, group_order: int, verify_threshold: int):

        public_values_dict = {
            "client_id": client_id,
            "vault_coefs": list(vault_coefs),
            "client_public_key_PEM": client_public_key_PEM,
            "group_order": group_order,
            "verify_threshold": verify_threshold,
        }

        return json.dumps(public_values_dict)

def run_tests():
    template_bottom_boundry = 1
    template_up_boundry = 8

    biometrics_template = [1,2,3,4,5,6,7,8] + [random.randint(template_bottom_boundry, template_up_boundry) for i in range(36)]

    id = 1
    client = Client(id, biometrics_template)
    G = Group(prime=12401)

    public_values_json = client.enrol(verify_threshold=8, G=G)

    print(public_values_json)

def main():
    run_tests()

if __name__ == "__main__":
    main()


"""
TODO:


"""