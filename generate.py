from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

key = rsa.generate_private_key(
    backend=default_backend(),
    public_exponent=65537,
    key_size=2048
)
with open("key.pem", 'wb') as file:
    
    private = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )
    file.write(private)

public_key = key.public_key()
with open("key.crt", 'wb') as file:
    
    public = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    file.write(public)

