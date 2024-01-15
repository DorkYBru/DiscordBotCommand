import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import uuid
import platform
import winreg


def get_system_info():
    system_info = f"System: {platform.system()} {platform.version()}\n"
    system_info += f"Machine: {platform.machine()}\n"
    system_info += f"Processor: {platform.processor()}"
    return system_info


def hash_password(password):
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


def generate_token():
    # Generate a random UUID as a token
    token = str(uuid.uuid4())
    return token


def encrypt_data(data, public_key):
    cipher_text = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return cipher_text


def save_to_registry(registry_key, value_name, value_data):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_BINARY, value_data)


# Example usage:
raw_system_info = get_system_info()
hashed_system_info = hash_password(raw_system_info)
stored_token = generate_token()

# Combine hashed system info and encrypted token
combined_data = f"{hashed_system_info}|{stored_token}"

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Encrypt the combined data
encrypted_combined_data = encrypt_data(combined_data, public_key)

# Hash the private key before saving (for educational purposes only, not recommended in practice)
hashed_private_key = hash_password(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
).decode())

# Save to the registry
registry_key = r"SOFTWARE\WinGetApi"
save_to_registry(registry_key, "encrypted_combined_data",
                 encrypted_combined_data)
save_to_registry(registry_key, "hashed_private_key", hashed_private_key)
