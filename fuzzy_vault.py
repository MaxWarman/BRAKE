import secrets
import random
import galois
import numpy as np
from group_poly import Group, GroupPoly


class FuzzyVault:
    def __init__(self, group_order: int, bio_template: list):
        """
        Fuzzy Vault class constructor, that returns Fuzzy Vault instantiation object

        Parameters:
            - group_order (int): Order of group the BRAKE protocol is executed in
            - bio_template (list): Biometric vector that contains properties of measured and processed biometric modality on Client's device

        Returns:
            - self (Fuzzy Vault): Fuzzy Vault class object
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
    def generate_secret_polynomial(
        cls, group_order: int, sec_poly_deg: int
    ) -> GroupPoly:
        """
        Generate secret polynomial in given finite field of certain order

        Parameters:
            - group_order (int): Order of group the BRAKE protocol is executed in
            - sec_poly_deg (int): Desired degree of generated secret polynomial

        Returns:
            - self (Fuzzy Vault): Fuzzy Vault class object
        """
        secret_coefs = np.array([], dtype=np.uint64)
        for i in range(sec_poly_deg):
            upper_bound = group_order - 1
            lower_bound = 0 if i != sec_poly_deg - 1 else 1

            rand_coef = int(
                secrets.randbelow(upper_bound - lower_bound + 1) + lower_bound
            )
            secret_coefs = np.append(secret_coefs, rand_coef)

        return GroupPoly(group_order, secret_coefs)

    def lock(self, secret_polynomial: GroupPoly = None) -> None:
        """
        Lock secret polynomial into Fuzzy Vault using biometric enrolment template provided by Client

        Parameters:
            - secret_polynomial (GroupPoly): Secret polynomial to be locked into Fuzzy Vault

        Returns:
            - None
        """
        # Encode biometric template into polynomial in finite field of order the same as in secret
        vault_polynomial = GroupPoly.one(self.group_order)
        for value in self.bio_template:
            multiplication_component = GroupPoly(self.group_order, [-value, 1])
            vault_polynomial = vault_polynomial * multiplication_component

        # Add secret polynomial to polynomial derived from Client's biometric template
        vault_polynomial = vault_polynomial + secret_polynomial
        self.vault_polynomial = vault_polynomial

    def get_random_argument_combinations(
        self, how_many_indices: int, how_many_combinations: int
    ) -> list:
        """
        Generate list of unique index combinations of length equal to the number of unlocking rounds. Unique combination contains indices of biometric template to use in specific unlocking round

        Parameters:
            - how_many_indices (int): How many indices to put into single combination, equivalent of verification threshold
            - how_many_combinations (int): How many unique combinations to generate, equivalent of number of unlocking rounds

        Returns:
            - unique_combinations_of_indices (list): List of all generated unique combinations of indices
        """
        # Define set of all indices in biometric template
        set_of_indices = set(range(self.bio_template_length))

        # Generate desired amount of unique combinations of indices of biometric template
        unique_combinations_of_indices = set()
        while len(unique_combinations_of_indices) < how_many_combinations:
            combination = tuple(sorted(random.sample(set_of_indices, how_many_indices)))
            unique_combinations_of_indices.add(combination)

        # Parse sets of combinations into lists
        unique_combinations_of_indices = list(unique_combinations_of_indices)
        for i, combination in enumerate(unique_combinations_of_indices):
            unique_combinations_of_indices[i] = list(combination)

        return list(unique_combinations_of_indices)

    def unlock(
        self, verify_threshold: int, number_of_unlocking_rounds: int = 5000
    ) -> GroupPoly:
        """
        Unlock secret polynomial from Fuzzy Vault using biometric verification template provided by Client

        Parameters:
            - verify_threshold (int): Number of (argument, value) pairs of Fuzzy Vault used to recover secret polynomial
            - number_of_unlocking_rounds (int): Number of secret polynomial recovery rounds to perform
        Returns:
            - secret_polynomial (GroupPoly): Recovered secret polynomial object
        """
        # Define Finite Field of order delivered to Client from Server
        GF = galois.GF(self.group_order)

        # Dictionary structure for counting occurence of certain secret polynomials during unlocking process
        poly_counting_dict = {}

        # Generate unique index combination list
        unique_index_combinations = self.get_random_argument_combinations(
            verify_threshold, number_of_unlocking_rounds
        )

        for combination in unique_index_combinations:
            arguments = GF([self.bio_template[ind] for ind in combination])
            values = [self.vault_polynomial.eval(int(arg)) for arg in arguments]
            values = GF(values)

            # Recover secret polynomial from chosen arguments 'x' and Fuzzy Vault values V(x) using Lagrange interpolation for finite field polynomials
            try:
                interpolated_polynomial = galois.lagrange_poly(arguments, values)
            except:
                continue

            # Count secret polynomial occurence
            secret_polynomial_coeffs = list(
                [
                    int(coefficient)
                    for coefficient in interpolated_polynomial.coefficients()[::-1]
                ]
            )
            if str(secret_polynomial_coeffs) not in poly_counting_dict.keys():
                poly_counting_dict[str(secret_polynomial_coeffs)] = 1
            else:
                poly_counting_dict[str(secret_polynomial_coeffs)] += 1

        # Choose most common ocurring polynomial as true recovered secret polynomial
        most_common_coefs_str = str(max(poly_counting_dict, key=poly_counting_dict.get))
        secret_polynomial_coeffs = [
            int(val)
            for val in most_common_coefs_str.replace("[", "")
            .replace("]", "")
            .split(", ")
        ]
        secret_polynomial = GroupPoly(
            group_order=self.group_order, coef=secret_polynomial_coeffs
        )

        return secret_polynomial

    def set_vault_polynomial(self, vault_polynomial_coefs: list) -> None:
        """
        Set vault polynomial as Fuzzy Vault object property

        Parameters:
            - vault_polynomial_coefs (list): List of coefficients of Fuzzy Vault polynomial

        Returns:
            - None
        """
        self.vault_polynomial = GroupPoly(
            group_order=self.group_order, coef=vault_polynomial_coefs
        )


def run_tests():
    print("Running fuzzy_vault.py tests...")
    DEBUG = True

    G = Group(prime=12401)
    enrol_bottom_boundry = 0
    enrol_top_boundry = 8

    enrol_template = [1, 2, 3, 4, 5, 6, 7, 8] + [
        random.randint(enrol_bottom_boundry, enrol_top_boundry) for i in range(36)
    ]
    verification_template = [1, 2, 3, 4, 5, 6, 7, 8]
    verify_threshold = len(verification_template)
    secret_polynomial = FuzzyVault.generate_secret_polynomial(
        group_order=G.order, sec_poly_deg=verify_threshold
    )

    fv = FuzzyVault(
        group_order=G.order,
        bio_template=enrol_template,
        secret_polynomial=secret_polynomial,
        verify_threshold=verify_threshold,
        DEBUG=DEBUG,
    )
    retrieved_secret_polynomial = FuzzyVault.unlock(
        fv, group_order=G.order, bio_template=verification_template
    )

    if DEBUG:
        print(fv)
        print(f"Retrieved secret polynomial: {retrieved_secret_polynomial}")

    assert secret_polynomial == retrieved_secret_polynomial

    print("\nTests completed!")


def main():
    run_tests()


if __name__ == "__main__":
    main()
