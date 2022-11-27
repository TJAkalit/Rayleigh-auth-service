from pydantic import BaseModel

class UserModel(BaseModel):
    
    id: int
    login: str
    password: str
    
class CredentialsModel(BaseModel):

    login: str
    password: str