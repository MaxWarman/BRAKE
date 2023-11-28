import random

from client import Client
from server import Server
from group_poly import Group

def main():
    # If debug_flag == True - enter verbose mode with additional messages during program execution
    debug_flag = True
    # If verify_only == True - the program will skip the enrolment phase
    verify_only = True
    # If erase_client == True - client's profile will be erased from server's database at the end of the program
    erase_client = False
    
    # Define constant values
    SERVER_DB_PATH = "./server_db/"
    ENROL_BOTTOM_BOUNDRY = 1
    ENROL_UP_BOUNDRY = 12400
    G = Group(prime=12401)
    bio_template_length = 44

    # Create authentication Server instance
    server = Server(SERVER_DB_PATH)

    if not verify_only:
        print("\n###### START ENROLMENT ######\n")
        
        # Create enrolment Client instance
        client_id = 1
        verify_threshold = 8
        client_enrolment_biometrics_template = [i for i in range(bio_template_length)]
        client_enrolment = Client(client_id, client_enrolment_biometrics_template)

        # Enrol Client to Server
        enrolment_json = client_enrolment.enrol(verify_threshold=verify_threshold, group=G, DEBUG=debug_flag)
        server.enrol_client(enrolment_json)
        
        print("\n###### END ENROLMENT ######\n")
    
    print("\n###### START VERIFICATION ######\n")
    
    # Create verification Client instance
    client_id = 1
    correct_samples = 22
    client_verification_biometrics_template = [i for i in range(correct_samples)] + [random.randint(ENROL_BOTTOM_BOUNDRY, ENROL_UP_BOUNDRY) for i in range(bio_template_length - correct_samples)]
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
    
    print("\n###### SESSION KEY EXCHANGE SUCCESSFUL ######\n")

    print(f"Exchanged session key value: {recovered_session_key}")

    if erase_client:
        print("\n###### CLEAN-UP STEP ######\n")
        server.delete_existing_user_by_id(client_id)

if __name__ == "__main__":
    main()