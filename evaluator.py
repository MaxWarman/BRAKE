import hashlib


class Evaluator:
    def __init__(self):
        """
        Evaluator class constructor, that returns Evaluator instantiation object

        Parameters:
            - None

        Returns:
            - self (Evaluator): Evaluator class object
        """

        # Set Evaluator's secret key
        secret_key = "evaluator_secret_key".encode("utf-8")
        self._secret_key = int(hashlib.sha256(secret_key).hexdigest(), 16)

        # Set Evaluator's OPRF moduli as the lowest prime number lower than maximal possible value for secret key
        self.mod = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF43

    def evaluate(self, input_value: str) -> str:
        """
        Evaluate blinded value using Evaluator's secret key.

        Parameters:
            - input_value (str): Value to be evaluated as hex string

        Returns:
            - evaluated_value_hex (str): Evaluated value of input as hex string
        """

        input_value_dec = int(input_value, 16)

        # Insecure evaluation not based on any known OPRF primitive scheme!
        evaluated_value_dec = (input_value_dec + self._secret_key) % self.mod
        evaluated_value_hex = hex(evaluated_value_dec)[2:]

        return evaluated_value_hex


def run_tests():
    input_value = hashlib.sha256(b"blinded_data").hexdigest()
    print(f"Input value [r]H(f): {input_value}")

    ev = Evaluator()
    val = ev.evaluate(input_value=input_value)
    print(f"Evaluation [k][r]H(f): {val}")


def main():
    run_tests()


if __name__ == "__main__":
    main()
