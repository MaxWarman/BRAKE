import hashlib
import numpy as np
from group_poly import Group

class Evaluator:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.mod = 0x10000000000000000000000000000000000000000000000000000000000000000
    
    def evaluate(self, input_value: str):
        input_value_dec = int(input_value, 16)
        evaluated_value_dec = pow(input_value_dec, self.secret_key, self.mod)
        evaluated_value_hex = hex(evaluated_value_dec)[2:]
        return evaluated_value_hex

def run_tests():
    print("evaluator.py")
    input_value = hashlib.sha256(b'tajne_dane').hexdigest()
    evaluator_secret_key = int(hashlib.sha256(b'tajny_klucz').hexdigest(), 16)
    print(f"Input value H(f)^r: {input_value}")
    ev = Evaluator(secret_key=evaluator_secret_key)
    val = ev.evaluate(input_value=input_value)
    print(f"Evaluation H(f)^(r*k): {val}")

def main():
    run_tests()

if __name__ == "__main__":
    main()