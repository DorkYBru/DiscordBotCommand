from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import winreg


def read_from_registry(registry_key, value_name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        return None


def decrypt_data(encrypted_data, private_key):
    plain_text = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()
    return plain_text


# Example usage:
registry_key = r"SOFTWARE\WinGetApi"
encrypted_combined_data = read_from_registry(
    registry_key, "encrypted_combined_data")
hashed_private_key = read_from_registry(registry_key, "hashed_private_key")

# Hash the private key (for educational purposes only, not recommended in practice)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
hashed_input_private_key = hash_password(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
).decode())

# Verify that the hashed private key matches the stored hashed private key
if hashed_input_private_key == hashed_private_key:
    print("Private key hash verification successful!")

    # Restore public key from bytes
    public_key = serialization.load_pem_public_key(read_from_registry(
        registry_key, "public_key"), backend=default_backend())

    # Perform decryption
    decrypted_combined_data = decrypt_data(
        encrypted_combined_data, private_key)

    # Split the combined data into hashed system info and encrypted token
    hashed_system_info, encrypted_token = decrypted_combined_data.split("|")

    # Perform authentication checks here using the decrypted values
    if hashed_system_info and encrypted_token:
        print("Decryption successful!")

        # Add your authentication logic here
        # Example: Authenticate system and user using the functions provided in the previous examples
        print(f"Hashed System Info: {hashed_system_info}")
        print(f"Encrypted Token: {encrypted_token}")
    else:
        print("Decryption failed!")
else:
    print("Private key hash verification failed!")
