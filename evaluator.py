import hashlib

class Evaluator:
    def __init__(self):
        """
        Evaluator class constructor, that returns Evaluator instantiation object

        Returns:
            self (Evaluator): Evaluator class object
        """

        # Proposed Evaluator model is not resistant to changing secret key value, thus the key has constant value
        self._secret_key = int(hashlib.sha256(b'evaluator_secret_key').hexdigest(), 16)
        self.mod = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff43
    
    def evaluate(self, input_value: str):
        """
        Evaluate blinded value using Evaluator's secret key.

        Parameters:
            input_value (str): Value to be evaluated as hex string
        
        Returns:
            evaluated_value_hex (str): Evaluated value of input as hex string
        """
        
        input_value_dec = int(input_value, 16)
        #evaluated_value_dec = pow(input_value_dec, self._secret_key, self.mod)
        evaluated_value_dec = (input_value_dec + self._secret_key) % self.mod
        evaluated_value_hex = hex(evaluated_value_dec)[2:]
        return evaluated_value_hex

def run_tests():
    print("evaluator.py")
    input_value = hashlib.sha256(b'blinded_data').hexdigest()
    print(f"Input value H(f)^r: {input_value}")
    
    ev = Evaluator()
    val = ev.evaluate(input_value=input_value)
    print(f"Evaluation H(f)^(r*k): {val}")

def main():
    run_tests()

if __name__ == "__main__":
    main()