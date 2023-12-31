import random

from client import Client
from server import Server
from group_poly import Group


def execute_BRAKE(correct_samples=None, number_of_unlocking_rounds=None):
    # If debug_flag == True - enter verbose mode with additional messages during program execution
    debug_flag = True
    # If verify_only == True - the program will skip the enrolment phase
    verify_only = False
    # If erase_client == True - client's profile will be erased from server's database after successful key exchange
    erase_client = True

    # Define constant values
    SERVER_DB_PATH = "./server_db/"
    
    # Set prime number 'q' and Group object with order 'q'
    PRIME = 2147483647
    G = Group(prime=PRIME)

    # Set boundries to randomly generate biometric template values from
    ENROL_BOTTOM_BOUNDRY = 1
    ENROL_UP_BOUNDRY = PRIME - 1

    # Set biometric template length
    bio_template_length = 44

    # Set number of correct samples corresponding with the enrolment template
    if correct_samples is None:
        correct_samples = 22

    # Set number of unlocking rounds to execute during verification phase
    if number_of_unlocking_rounds is None:
        number_of_unlocking_rounds = 5000

    # Create authentication Server instance
    server = Server(SERVER_DB_PATH)

    if not verify_only:
        print("\n###### START ENROLMENT ######\n")

        # Create enrolment Client instance
        client_id = 1
        verify_threshold = 8
        client_enrolment_biometrics_template = [
            random.randint(ENROL_BOTTOM_BOUNDRY, ENROL_UP_BOUNDRY)
            for i in range(bio_template_length)
        ]
        random.shuffle(client_enrolment_biometrics_template)
        client_enrolment = Client(client_id, client_enrolment_biometrics_template)

        # Enrol Client to Server
        enrolment_json = client_enrolment.enrol(
            verify_threshold=verify_threshold, group=G, DEBUG=debug_flag
        )
        server.enrol_client(enrolment_json)

        print("\n###### END ENROLMENT ######\n")

    print("\n###### START VERIFICATION ######\n")

    # Create verification Client instance
    client_id = 1
    client_verification_biometrics_template = list(
        client_enrolment_biometrics_template[:correct_samples]
    ) + [
        random.randint(ENROL_BOTTOM_BOUNDRY, ENROL_UP_BOUNDRY)
        for i in range(bio_template_length - correct_samples)
    ]
    random.shuffle(client_verification_biometrics_template)
    client_verification = Client(client_id, client_verification_biometrics_template)

    # Send client request for public data
    verify_json = server.vault_request(client_id=client_verification.id)

    # Verify Client with Server, recover Client's private key
    client_private_key_PEM = client_verification.verify(
        public_values_json=verify_json,
        group=G,
        number_of_unlocking_rounds=number_of_unlocking_rounds,
        DEBUG=debug_flag,
    )

    print("\n###### END VERIFICATION ######\n")

    print("\n###### START KEY EXCHANGE ######\n")

    # Establish session key
    encrypted_session_key, session_key_hash = server.send_session_key_to_client(
        client_id=client_verification.id, DEBUG=debug_flag
    )
    recovered_session_key = client_verification.recover_session_key(
        encrypted_session_key=encrypted_session_key,
        client_private_key_PEM=client_private_key_PEM,
    )
    recovered_session_key_hash = client_verification.get_session_key_hash(
        recovered_session_key
    )

    # Assert if session key hashes are the same
    if debug_flag:
        print("\nRunning session key hashes comparison assertion...")
    assert recovered_session_key_hash == session_key_hash

    print("\n###### SESSION KEY EXCHANGE SUCCESSFUL ######\n")

    if debug_flag:
        print(f"Exchanged session key value: {recovered_session_key}")
    
    print("\n###### END KEY EXCHANGE ######\n")


    if erase_client:
        print("\n###### CLEAN-UP STEP ######\n")
        server.delete_existing_user_by_id(client_id)


def main():
    execute_BRAKE()


if __name__ == "__main__":
    main()
