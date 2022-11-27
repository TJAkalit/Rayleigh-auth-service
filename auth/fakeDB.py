from .models import UserModel
from .funcs import encodePassword

userTable = {
    'admin': UserModel(
        id=1,
        login='admin',
        password=encodePassword('123456')
    ),
    'moder': UserModel(
        id=2,
        login='moder',
        password=encodePassword('654321')
    ),
}

userTableById: dict = {
    userTable[x].id: userTable[x] for x in userTable
}
