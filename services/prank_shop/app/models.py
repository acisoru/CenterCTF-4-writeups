from pydantic import BaseModel

class ItemInDb(BaseModel):
    name: str
    price: int
    owner: int
    item_id: int
    description: str #

class ItemInput(BaseModel):
    name: str
    price: int
    # owner: int
    # item_id: int
    description: str

class User(BaseModel):
    id: int
    balance: int
    username: str

