from fastapi import (
    FastAPI, 
    Request,
)
from pydantic import BaseModel
from fastapi import HTTPException

class UserModel(BaseModel):
    
    id: int
    name: str
    roles: list[int]
    
fakeUserDB = {
    1: UserModel(
        **{
            'id': 1,
            'name': 'admin',
            'roles': [1, ],
        }
    ),
    2: UserModel(
        **{
            'id': 2,
            'name': 'moder',
            'roles': [1, 2, 3,],
        }
    ),
}

rolesAPI = FastAPI()

@rolesAPI.get('/{user_id}')
async def index(user_id: int | None):
    
    user = fakeUserDB.get(user_id)
    if not user:
        raise HTTPException(404, 'User don\'t exists')
    
    return user

@rolesAPI.middleware('http')
async def verify_token(request: Request, call_next):
    token = request.cookies.get('int')
    print(request.cookies)
    response = await call_next(request)
    return response
