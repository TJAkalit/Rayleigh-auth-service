import jwt
from fastapi import (
    FastAPI,
    Response,
    HTTPException,
    Cookie,
)
from pathlib import Path
from os import environ
from logging import getLogger
from datetime import (
    timedelta,
    timezone,
    datetime,
)
from .models import (
    UserModel,
    CredentialsModel,
)
from .fakeDB import userTable, userTableById
from .funcs import encodePassword

_log = getLogger('Rayleigh.auth')

class PrivateKeyNotExists(Exception):
    pass

def loadKey(path: Path) -> bytes:
    """_summary_

    Args:
        path (Path): путь к файлу, который необходимо загрузить

    Returns:
        bytes: байтовое представление файла ключа
    """
    
    with open(path, 'rb') as file:
        return file.read()

def loadKeyByEnv(envKey: str, defValue: str) -> bytes:
    """_summary_

    Args:
        envKey (str): ключ переменной окружения
        defValue (str): значение по-умолчанию

    Raises:
        PrivateKeyNotExists: файл ключа не найден

    Returns:
        bytes: байтовое представление файла ключа
    """

    envValue = environ.get(envKey, defValue)
    _log.info(f'Env[{envKey:s}]=[{envValue:s}]')
    _tryPk0 = Path(envValue)
    _tryPk1 = Path('./' + envValue)

    key = None

    if _tryPk0.exists():
        key = loadKey(_tryPk0)
        _log.info(f"Loaded key \'{_tryPk0}\'")
        
    if _tryPk1.exists() and not key:
        key = loadKey(_tryPk1)
        _log.info(f"Loaded key \'{_tryPk1}\'")
    
    if not key:
        _log.error(f"Tried to find keys: [{_tryPk0:s}, {_tryPk1:s}] but it's failed")
        raise PrivateKeyNotExists(f"Tried to find keys: [{_tryPk0:s}, {_tryPk1:s}] but it's failed")
    
    return key

def loadIntegerEnv(envKey: str, defValue: int) -> int:
    """_summary_

    Args:
        envKey (str): ключ переменной окружения
        defValue (int): значение по-умолчанию
    
    Raises:
        ValueError: полученное значение невозможно конвертировать в целочисленное

    Returns:
        int: числовое значение переменной
    """
    envValue: str = environ.get(envKey, defValue)
    _log.info(f'Env[{envKey:s}]=[{envValue:d}]')
    if envValue.__class__ is not int:
        if not envValue.isdigit():
            _log.error(f'Env[{envKey:s}] is not convertable to integer')
    return int(envValue)

def getJWT(user: UserModel, refresh: bool = False) -> str:

    payload = {
        'id': user.id,
    }
    if refresh:
        # Refresh token
        payload['exp'] = int(
            (datetime.now(appTimezone) + aliveRefreshTime).timestamp()
        )
    else:
        # Access token
        payload['login'] = user.login
        payload['exp'] = int(
            (datetime.now(appTimezone) + aliveAccessTime).timestamp()
        )
    return jwt.encode(
        payload=payload,
        key=privateKey,
        algorithm='RS256',
    )
    
def verifyJWT(token: str) -> dict:

    try:
        data = jwt.decode(token, key=publicKey, algorithms=['RS256'])
    except Exception as ex:
        # TODO: детальная обработка ошибок
        return None
    return data

_log.info('Begin initiate private key')
privateKey = loadKeyByEnv('AUTH_PRIVATE_KEY', 'auth.pem')
"""
Файл приватного ключа для модуля auth
"""

_log.info('Begin initiate public key')
publicKey = loadKeyByEnv('AUTH_PUBLIC_KEY', 'auth.crt')
"""
Файл публичного ключа для модуля auth
"""

_log.info('Begin initiate UTC timezone')
_utcDelta = loadIntegerEnv('AUTH_UTC_DELAY_HOURS', 3)
_utcName = environ.get("AUTH_UTC_NAME", 'Europe/Moscow')
appTimezone = timezone(timedelta(hours=_utcDelta), name=_utcName)
"""
Объект часового пояса
"""

_aliveRefreshTime = loadIntegerEnv('AUTH_REFRESH_TTL', 600)
aliveRefreshTime = timedelta(seconds=_aliveRefreshTime)
"""
Объект временного отступа для срока валидности refresh токена
"""

_aliveAccessTime = loadIntegerEnv(
    'AUTH_ACCESS_TTL', int(_aliveRefreshTime/20)
)
aliveAccessTime = timedelta(seconds=_aliveAccessTime)
"""
Объект временного отступа для срока валидности access токена
"""

authAPI = FastAPI()

@authAPI.post('/login')
async def login(response: Response, creds: CredentialsModel):
    """
    Выдать access и refresh токены на основе вводимых даных пользователя
    """
    user = userTable.get(creds.login)
    if not user:
        raise HTTPException(401, 'Wrong login or password')
    if user.password!=encodePassword(creds.password):
        raise HTTPException(401, 'Wrong login or password')

    accessToken = getJWT(user)
    refreshToken = getJWT(user, refresh=True)
    
    response.set_cookie(
        key='RayleightRefresh',
        value=refreshToken,
        expires=int(
            (datetime.now(appTimezone) + aliveRefreshTime).timestamp()
        ),
        path='/auth/login',
        httponly=True,
        domain='127.0.0.1',
    )

    return {
        "token": accessToken,
    }

@authAPI.get('/login')
async def refresh(
    response: Response,
    RayleightRefresh: str|None = Cookie(default=None),
):
    if not RayleightRefresh:
        raise HTTPException(401, 'missing refresh token')
    data = verifyJWT(RayleightRefresh)
    if not data:
        raise HTTPException(401, 'false refresh token')
    
    user = userTableById.get(data['id'])
    
    if not user:
        raise HTTPException(401, 'false refresh token')
    
    accessToken = getJWT(user)
    refreshToken = getJWT(user, refresh=True)
    
    response.set_cookie(
        key='RayleightRefresh',
        value=refreshToken,
        expires=int(
            (datetime.now(appTimezone) + aliveRefreshTime).timestamp()
        ),
        path='/auth/login',
        httponly=True,
        domain='127.0.0.1',
    )

    return {
        "token": accessToken,
    }


    
