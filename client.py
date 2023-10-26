import random
import hashlib
import json

from rsa import generate_key
from evaluator import Evaluator
from fuzzy_vault import FuzzyVault
from group_poly import Group, GroupPoly
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class Client:

    def __init__(self, client_id: int, biometrics_template: list):
        self.id = client_id
        self.biometrics_template = biometrics_template

    def enrol(self, verify_threshold: int, group: Group, DEBUG=False) -> str:
        # Generate secret polynomial for the Client with given ID
        secret_polynomial = FuzzyVault.generate_secret_polynomial(group_order=group.order, sec_poly_deg=verify_threshold)

        # Create FuzzyVault using secret polynomial and lock it
        fuzzy_vault = FuzzyVault(group_order=group.order, bio_template=self.biometrics_template)#, secret_polynomial=secret_polynomial, verify_threshold=verify_threshold, DEBUG=DEBUG)
        fuzzy_vault.lock(secret_polynomial=secret_polynomial)

        # Evaluate OPRF with Evaluator
        unblinded_evaluator_result = self.evaluate(secret_polynomial=secret_polynomial, group=group, DEBUG=DEBUG)
        
        # Generate seeded client key pair: [0] - private, [1] - public
        client_public_key_PEM = self.generate_key_pair_PEM(unblinded_evaluator_result=unblinded_evaluator_result)[1]

        # Send (id, V(x), cpk_t) to the server
        public_values_json = self.create_public_values_json(fuzzy_vault.vault_polynomial.coef.tolist(), client_public_key_PEM, group.order, verify_threshold)
        
        # Print values for debugging purpose
        if DEBUG:
            print(f"secret poly: {secret_polynomial}")
            print(f"unblinded poly: {unblinded_evaluator_result}\n")
            print(f"public values json: {public_values_json}")

        return public_values_json
    
    def verify(self, public_values_json: str, group: Group, DEBUG=False) -> str:
        # Convert json of public values into dict
        public_values_dict = self.create_public_values_dict(public_values_json=public_values_json)
        
        group_order = public_values_dict["group_order"]
        verify_threshold = public_values_dict["verify_threshold"]

        # Create FuzzyVault instance for verification purpose
        fuzzy_vault = FuzzyVault(group_order=group_order, bio_template=self.biometrics_template)
        fuzzy_vault.set_vault_polynomial(vault_polynomial_coefs=public_values_dict["vault_coefs"])

        # Unlock vault using 
        recovered_secret_polynomial = fuzzy_vault.unlock(verify_threshold=verify_threshold)

        # Evaluate OPRF with Evaluator
        unblinded_evaluator_result = self.evaluate(secret_polynomial=recovered_secret_polynomial, group=group, DEBUG=DEBUG)

        client_private_key_PEM, client_public_key_PEM = self.generate_key_pair_PEM(unblinded_evaluator_result=unblinded_evaluator_result)

        if DEBUG:
            print(f"public values json: {public_values_json}\n")
            print(f"secret poly: {recovered_secret_polynomial}")
            print(f"unblinded poly: {unblinded_evaluator_result}")

            print(f"recovered public key\n{client_public_key_PEM}")

        return client_private_key_PEM

    def recover_session_key(self, encrypted_session_key: bytes, client_private_key_PEM: str) -> bytes:
        client_private_key = RSA.import_key(client_private_key_PEM)
        cipher = PKCS1_OAEP.new(client_private_key)

        session_key = cipher.decrypt(encrypted_session_key)

        return session_key
    
    def get_session_key_hash(self, session_key: bytes) -> str:
        return hashlib.sha256(session_key).hexdigest()

    def evaluate(self, secret_polynomial: GroupPoly, group: Group, DEBUG=False):
        # Gennerate blinding exponent and its multiplicative inverse
        r, r_inv, r_mod = Client.generate_blinding_exponent()
        assert((r * r_inv)%r_mod == 1)

        # Blind secret polynomial
        blinded_polynomial = Client.blind(secret_polynomial, r, r_mod, DEBUG=DEBUG)

        # Evaluate blinded polynomial with Evaluator 
        evaluator = Evaluator()
        evaluated_polynomial = evaluator.evaluate(blinded_polynomial)

        # Unblind result returned by the Evaluator
        # r_inv = -r % r_mod
        r_inv = group.order - 1 - r
        unblinded_evaluator_result = Client.unblind(evaluated_polynomial, r_inv, r_mod, DEBUG=DEBUG)

        return unblinded_evaluator_result

    def generate_key_pair_PEM(self, unblinded_evaluator_result: str) -> tuple:
        client_private_key = generate_key(unblinded_evaluator_result)
        client_private_key_PEM = client_private_key.export_key("PEM").decode("utf-8")
        client_public_key_PEM = client_private_key.publickey().exportKey("PEM").decode("utf-8")

        return (client_private_key_PEM, client_public_key_PEM)

    @classmethod
    def blind(cls, secret_polynomial, r, r_mod, DEBUG) -> str:
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
    def unblind(cls, evaluated_polynomial, r_inv, r_mod, DEBUG) -> tuple:
        evaluated_polynomial_int = int(evaluated_polynomial, 16)
        
        #unblind = pow(evaluated_polynomial_int, r_inv, r_mod)
        unblind = (evaluated_polynomial_int + r_inv) % r_mod
        unblind = hex(unblind)[2:]

        return unblind

    @classmethod
    def generate_blinding_exponent(cls) -> tuple:
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
    
    def create_public_values_json(self, vault_coefs: list, client_public_key_PEM: str, group_order: int, verify_threshold: int) -> str:

        public_values_dict = {
            "client_id": self.id,
            "vault_coefs": list(vault_coefs),
            "client_public_key_PEM": client_public_key_PEM,
            "group_order": group_order,
            "verify_threshold": verify_threshold,
        }

        return json.dumps(public_values_dict)
    
    def create_public_values_dict(self, public_values_json):
        return json.loads(public_values_json)

def run_tests():
    debug_flag = True
    template_bottom_boundry = 1
    template_up_boundry = 8

    biometrics_template = [1,2,3,4,5,6,7,8] + [random.randint(template_bottom_boundry, template_up_boundry) for i in range(36)]

    id = 1
    client = Client(id, biometrics_template)
    G = Group(prime=12401)

    public_values_json = client.enrol(verify_threshold=8, group=G, DEBUG=debug_flag)


def main():
    run_tests()

if __name__ == "__main__":
    main()


"""
TODO:


"""