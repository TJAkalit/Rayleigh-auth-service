from hashlib import sha256

def encodePassword(password: str) -> str:
    
    return sha256(password.encode('utf-8')).hexdigest()