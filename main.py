from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def index():
    
    return {'Hello, world!': 'from me'}

from roles import rolesAPI

app.mount('/roles', rolesAPI)

