import os
import json

class Server:
    def __init__(self, db_path: str):
        """
        Server class constructor, that returns Server instantiation object

        Parameters:
            db_path (str): Path to directory that stores parameters of enroled clients.

        Returns:
            self (Server): Server object
        """

        self.db_path = db_path
        if not os.path.exists(self.db_path):
            print(f"Server: creating database directory {self.db_path}")
            os.makedirs(self.db_path)

    def enrol_client(self, client_enrolment_json: str):
        """
        Saving enroled client data to server database.

        Parameters:
            client_enrolment_json (str): Enrolment data received from client to be stored at the server.

        Returns:
            nothing
        """
        client_enrolment_dict = json.loads(client_enrolment_json)
        
        client_id = client_enrolment_dict["client_id"]
        for filename in os.listdir(self.db_path):
            if filename == f"{client_id}.json":
                raise FileExistsError(f"Submitted Client ID {client_id} already exists!")
        
        with open(f"{self.db_path}/{client_id}.json", "w") as f:
            f.write(client_enrolment_json)

def run_tests():
    SERVER_DB_PATH = "./server_db/"
    s = Server(SERVER_DB_PATH)

def main():
    run_tests()

if __name__ == "__main__":
    main()