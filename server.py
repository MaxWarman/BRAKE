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
            db_path (str): Path to directory that stores parameters of enroled clients.

        Returns:
            self (Server): Server class object
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

    def delete_existing_RSA_keys(self):
        file_to_delete = self.private_key_filepath
        try:
            os.unlink(file_to_delete)
        except:
            print(f"Could not delete {file_to_delete}: File does not exist")
        
        file_to_delete = self.public_key_filepath
        try:
            os.unlink(file_to_delete)
        except:
            print(f"Could not delete {file_to_delete}: File does not exist")

    def delete_existing_user_by_id(self, id):
        file_to_delete = f"{self.db_path}{id}.json"
        try:
            os.unlink(file_to_delete)
        except:
            print(f"Could not delete {file_to_delete}: File does not exist")

    def generate_RSA_key_pair(self):
        key = RSA.generate(self.RSA_key_size)
        server_private_key_pem = key.export_key("PEM").decode("utf-8")
        server_public_key_pem = key.publickey().export_key("PEM").decode("utf-8")

        with open(self.private_key_filepath, "wt") as f:
            f.write(server_private_key_pem)

        with open(self.public_key_filepath, "wt") as f:
            f.write(server_public_key_pem)

    def client_exists(self, client_id) -> bool:
        db_file_list = os.listdir(self.db_path)
        return (f"{client_id}.json" in db_file_list)

    def RSA_key_pair_exists(self) -> bool:
        db_file_list = os.listdir(self.db_path)
        return (self.private_key_filename in db_file_list) and (self.public_key_filename in db_file_list)
        
    def generate_session_key(self) -> bytes:
        session_key_random_bytes = secrets.token_bytes(self.session_key_byte_length)
        session_key_salt = secrets.token_bytes(16)
        
        kdf_core = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=session_key_salt, iterations=100000,backend=default_backend())
        session_key = kdf_core.derive(session_key_random_bytes)
        
        return session_key
    
    def get_client_data_dict(self, client_id: int):
        with open(f"{self.db_path}{client_id}.json") as f:
            client_data_json = f.read()

        return json.loads(client_data_json)

    def send_session_key_to_client(self, client_id: int) -> tuple:
        session_key = self.generate_session_key()
        session_key_hash = hashlib.sha256(session_key).hexdigest()

        client_public_key = RSA.import_key(self.get_client_data_dict(client_id)["client_public_key_PEM"])
        cipher = PKCS1_OAEP.new(client_public_key)

        encrypted_session_key = cipher.encrypt(session_key)

        return (encrypted_session_key, session_key_hash)

    def enrol_client(self, client_enrolment_json: str) -> None:
        """
        Saving enroled client data to server database as .json file.

        Parameters:
            client_enrolment_json (str): Enrolment data received from client to be stored at the server.

        Returns:
            nothing
        """
        client_enrolment_dict = json.loads(client_enrolment_json)
        
        client_id = client_enrolment_dict["client_id"]
        if self.client_exists(client_id=client_id):
            print(f"Submitted Client ID {client_id} already exists! Returning None...")
            return None
        
        with open(f"{self.db_path}/{client_id}.json", "w") as f:
            f.write(client_enrolment_json)

    def vault_request(self, client_id: int) -> str:
        if not self.client_exists(client_id=client_id):
            raise FileNotFoundError(f"Submitted Client ID {client_id} is not in Server's database! Please enrol Client...")
        
        with open(f"{self.db_path}/{client_id}.json", "rt") as f:
            server_public_client_data_json = f.read()

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