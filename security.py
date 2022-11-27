from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key 
import jwt
from fastapi import Request

with open('key.pem', 'rb') as file:
    
    private = file.read()
    
with open('key.crt', 'rb') as file:
    
    public = file.read()

encoded = jwt.encode(
    payload={
        'test': 'str',
    },
    key=private,
    algorithm='RS256',
)
print(encoded)

data = jwt.decode(
    jwt=encoded,
    key=public,
    algorithms=['RS256'],
    verify=True,
)

print(data)