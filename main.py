from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()

@app.get('/')
async def index():
    
    return {'Hello, world!': 'from me'}

from roles import rolesAPI

app.mount('/roles', rolesAPI)

from auth import authAPI

app.mount('/auth', authAPI)