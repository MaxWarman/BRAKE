import random

from client import Client
from server import Server
from group_poly import Group

def main():
    # Flag for debugging purpose
    debug_flag = True
    
    # Define constant values
    SERVER_DB_PATH = "./server_db/"
    ENROL_BOTTOM_BOUNDRY = 1
    ENROL_UP_BOUNDRY = 8
    
    # Create authentication Server instance
    server = Server(SERVER_DB_PATH)

    print("\n###### START ENROLMENT ######\n")
    
    # Create enrolment Client instance
    client_id = 1
    verify_threshold = 8
    client_enrolment_biometrics_template = [i for i in range(44)] #[1,2,3,4,5,6,7,8] + [random.randint(ENROL_BOTTOM_BOUNDRY, ENROL_UP_BOUNDRY) for i in range(36)]
    G = Group(prime=12401)
    client_enrolment = Client(client_id, client_enrolment_biometrics_template)

    # Enrol Client to Server
    enrolment_json = client_enrolment.enrol(verify_threshold=verify_threshold, group=G, DEBUG=debug_flag)
    server.enrol_client(enrolment_json)
    
    print("\n###### END ENROLMENT ######\n")
    
    print("\n###### START VERIFICATION ######\n")
    
    # Create verification Client instance
    client_id = 1
    client_verification_biometrics_template = [i for i in range(44)] #[1,2,3,4,5,6,7,8] + [random.randint(ENROL_BOTTOM_BOUNDRY, ENROL_UP_BOUNDRY) for i in range(36)]
    client_verification = Client(client_id, client_verification_biometrics_template)

    # Send client request for public data
    verify_json = server.vault_request(client_id=client_verification.id)
    
    # Verify Client with Server, recover Client's private key
    client_private_key_PEM = client_verification.verify(public_values_json=verify_json, group=G, DEBUG=debug_flag)
    
    print("\n###### END VERIFICATION ######\n")

    print("\n###### START KEY EXCHANGE ######\n")

    # Establish session key
    encrypted_session_key, session_key_hash = server.send_session_key_to_client(client_id=client_verification.id)
    recovered_session_key = client_verification.recover_session_key(encrypted_session_key=encrypted_session_key, client_private_key_PEM=client_private_key_PEM)
    recovered_session_key_hash = client_verification.get_session_key_hash(recovered_session_key)
    
    print("\n###### END KEY EXCHANGE ######\n")

    # Assert if session keys are the same
    assert(recovered_session_key_hash == session_key_hash)
    
    print("###### SESSION KEY EXCHANGE SUCCESSFUL ######")


if __name__ == "__main__":
    main()