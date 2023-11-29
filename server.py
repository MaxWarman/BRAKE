import os
import json
import secrets
import hashlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Server:
    def __init__(self, db_path: str):
        """
        Server class constructor, that returns Server instantiation object

        Parameters:
            - db_path (str): Path to directory that stores parameters of enroled clients.

        Returns:
            - self (Server): Server class object
        """
        self.db_path = db_path
        self.RSA_key_size = 2048
        self.session_key_byte_length = 2048 // 8
        self.private_key_filename = "server_private_key.pem"
        self.private_key_filepath = f"{self.db_path}server_private_key.pem"
        self.public_key_filename = "server_public_key.pem"
        self.public_key_filepath = f"{self.db_path}server_public_key.pem"

        # Create Server's database if nonexistent
        if not os.path.exists(self.db_path):
            print(f"Server: creating database directory {self.db_path}")
            os.makedirs(self.db_path)

        # Generate Server's RSA key pair if nonexistent
        if not self.RSA_key_pair_exists():
            self.delete_existing_RSA_keys()
            self.generate_RSA_key_pair()

    def delete_existing_RSA_keys(self) -> None:
        """
        Search Server's database for Server's RSA keys and delete them if found

        Parameters:
            - None

        Returns:
            - None
        """

        # Find and delete private key file
        file_to_delete = self.private_key_filepath
        try:
            os.unlink(file_to_delete)
        except:
            print(f"Could not delete {file_to_delete}: File does not exist")
        
        # Find and delete public key file
        file_to_delete = self.public_key_filepath
        try:
            os.unlink(file_to_delete)
        except:
            print(f"Could not delete {file_to_delete}: File does not exist")

    def delete_existing_user_by_id(self, id: int) -> None:
        """
        Search Server's database for Client's profile identified by 'id'  and delete it if found

        Parameters:
            - client_id (int): Client's identificator

        Returns:
            - None
        """
        
        # Find and delete Client's profile
        file_to_delete = f"{self.db_path}{id}.json"
        try:
            os.unlink(file_to_delete)
        except:
            print(f"Could not delete {file_to_delete}: File does not exist")

    def generate_RSA_key_pair(self) -> None:
        """
        Generate new RSA key pair for Server and store it in Server's database

        Parameters:
            - client_id (int): Client's identificator

        Returns:
            - None
        """

        # Generate RSA key pair
        key = RSA.generate(self.RSA_key_size)
        server_private_key_pem = key.export_key("PEM").decode("utf-8")
        server_public_key_pem = key.publickey().export_key("PEM").decode("utf-8")

        # Save generated keys to Server's database
        with open(self.private_key_filepath, "wt") as f:
            f.write(server_private_key_pem)

        with open(self.public_key_filepath, "wt") as f:
            f.write(server_public_key_pem)

    def client_exists(self, client_id) -> bool:
        """
        Check whether Client profile with certain 'id' exists in Server's database

        Parameters:
            - client_id (int): Client's identificator

        Returns:
            - (bool): Logic value of Client existence in Server's database
        """
        db_file_list = os.listdir(self.db_path)
        return (f"{client_id}.json" in db_file_list)

    def RSA_key_pair_exists(self) -> bool:
        """
        Check whether Server's RSA key pair exists in Server's database

        Parameters:
            - None

        Returns:
            - (bool): Logic value of key pair existence in Server's database
        """
        db_file_list = os.listdir(self.db_path)
        return (self.private_key_filename in db_file_list) and (self.public_key_filename in db_file_list)
        
    def generate_session_key(self) -> bytes:
        """
        Generate session key using PBKDF2HMAC cryptographic method

        Parameters:
            - None

        Returns:
            - (bytes): Value of generated session key
        """
        # Generate session key using PBKDF2HMAC KFD function
        session_key_random_bytes = secrets.token_bytes(self.session_key_byte_length)
        session_key_salt = secrets.token_bytes(16)
        kdf_core = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=session_key_salt, iterations=100000,backend=default_backend())
        session_key = kdf_core.derive(session_key_random_bytes)
        
        return session_key
    
    def get_client_data_dict(self, client_id: int) -> dict:
        """
        Generate session key using PBKDF2HMAC cryptographic method

        Parameters:
            - client_id (int): Client's identificator

        Returns:
            - (dict): Dictionary of Client's profile stored in Server's database
        """
        with open(f"{self.db_path}{client_id}.json") as f:
            client_data_json = f.read()

        return json.loads(client_data_json)

    def send_session_key_to_client(self, client_id: int, DEBUG: bool = False) -> tuple:
        """
        Simulate sending encapsulated session key and it's checksum value to Client 

        Parameters:
            - client_id (int): Client's identificator
            - DEBUG (bool): Flag for verbose execution mode

        Returns:
            - (tuple):
                - encrypted_session_key (srt): Value of encapsulated session key
                - session_key_hash (str): Value of SHA256 checksum of session key
        """
        # Generate session key
        session_key = self.generate_session_key()
        if DEBUG:
            print(f"Session key generated by Server: {session_key}")

        # Compute SHA256 checksum of session key
        session_key_hash = hashlib.sha256(session_key).hexdigest()

        # Encapsulate session key using Client's public key obtained during enrolment phase
        client_public_key = RSA.import_key(self.get_client_data_dict(client_id)["client_public_key_PEM"])
        cipher = PKCS1_OAEP.new(client_public_key)
        encrypted_session_key = cipher.encrypt(session_key)

        return (encrypted_session_key, session_key_hash)

    def enrol_client(self, client_enrolment_json: str) -> None:
        """
        Saving enroled client data to server database as .json file.

        Parameters:
            client_enrolment_json (str): Enrolment data received from client to be stored at the Server

        Returns:
            - None
        """
        # Process Client's profile data
        client_enrolment_dict = json.loads(client_enrolment_json)
        client_id = client_enrolment_dict["client_id"]
        
        if self.client_exists(client_id=client_id):
            print(f"Submitted Client ID {client_id} already exists! Returning None...")
            return None
        
        # Save Client's profile into Server's database
        with open(f"{self.db_path}/{client_id}.json", "w") as f:
            f.write(client_enrolment_json)

    def vault_request(self, client_id: int) -> str:
        """
        Simulate Client's request for data stored in their profile in Server's database

        Parameters:
            - client_id (int): Client's identificator

        Returns:
            - public_verification_data_json (str): Content of public parameters stored in Server's database that are sent to Client in form of JSON
        """
        if not self.client_exists(client_id=client_id):
            raise FileNotFoundError(f"Submitted Client ID {client_id} is not in Server's database! Please enrol Client...")
        
        # Read Client's profile data
        with open(f"{self.db_path}/{client_id}.json", "rt") as f:
            server_public_client_data_json = f.read()

        # Create Clients public data as JSON 
        public_verication_dict = json.loads(server_public_client_data_json)
        public_verification_data_dict = {key : public_verication_dict[key] for key in public_verication_dict.keys() if key not in ("client_public_key_PEM")}
        public_verification_data_json = json.dumps(public_verification_data_dict)

        return public_verification_data_json

def run_tests():
    SERVER_DB_PATH = "./server_db/"
    s = Server(SERVER_DB_PATH)

def main():
    run_tests()

if __name__ == "__main__":
    main()