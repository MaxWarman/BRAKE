import random

from client import Client
from server import Server
from group_poly import Group

def main():
    # Define constant values
    SERVER_DB_PATH = "./server_db/"
    ENROL_BOTTOM_BOUNDRY = 1
    ENROL_UP_BOUNDRY = 8

    # Create client instance
    client_id = 1
    verification_threshold = 8
    client_enrolment_biometrics_template = [1,2,3,4,5,6,7,8] + [random.randint(ENROL_BOTTOM_BOUNDRY, ENROL_UP_BOUNDRY) for i in range(36)]
    G = Group(prime=12401)
    client = Client(client_id, client_enrolment_biometrics_template)

    # Enrol client
    enrolment_json = client.enrol(verification_threshold, G)
    server = Server(SERVER_DB_PATH)
    server.enrol_client(enrolment_json)
    


if __name__ == "__main__":
    main()