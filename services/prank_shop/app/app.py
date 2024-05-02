from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import app.db as db
from app.models import User,ItemInput,ItemInDb
import jwt
from datetime import datetime, timedelta
from typing import Annotated
import os


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.urandom(6).hex()
ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(hours=8)

def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload  = verify_jwt_token(token)
    if not payload :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload['sub']
    id, balance = db.con.execute("SELECT id,balance FROM Users WHERE username = ? ", (username,)).fetchone()
    return User(id=id,balance=balance,username=username)


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    cursor = db.con.cursor()
    result = db.check_password(cursor,form_data.username, form_data.password)
    if not result:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    cursor.close()
    return {"access_token": create_jwt_token({"sub":form_data.username}), "token_type": "bearer"}

@app.get("/users/")
def list_users() -> list[User]:
    cursor = db.con.cursor()
    users = db.get_users(cursor)
    cursor.close()
    return users

@app.get("/users/last/")
def list_last_users() -> list[User]:
    cursor = db.con.cursor()
    users = db.get_last_users(cursor)
    cursor.close()
    return users

@app.post("/users/register")
def register_user(username: str, password: str) -> User:
    try:
        cursor = db.con.cursor()
        user = db.create_user(cursor,username,password)
        cursor.close()
    except:
        raise HTTPException(status_code=400, detail="User already exists")
    return user

@app.get("/users/me/",response_model=User)
def current_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@app.get("/users/{id}")
def get_user(id: int) -> User:
    cursor = db.con.cursor()
    user = db.get_user_by_id(cursor,id)
    cursor.close()
    return user

@app.get("/users/me/items")
def current_user_items(current_user: Annotated[User, Depends(get_current_user)]) -> list[ItemInDb]:
    cursor = db.con.cursor()
    items = db.get_user_items(cursor, current_user.id)
    cursor.close()
    return items

@app.get("/users/{id}/items")
def get_user_items(id: int,current_user: Annotated[User, Depends(get_current_user)]) -> list[ItemInDb]:
    try: 
        cursor = db.con.cursor()
        items = db.get_user_items(cursor,id)
        cursor.close()
    except:
        raise HTTPException(status_code=404, detail="User not found")
    if id != current_user.id:
        for item in items:
            item.description = "REDACTED"
    return items

@app.get("/users/{id}/items")
def get_user_items(id: int,current_user: Annotated[User, Depends(get_current_user)]) -> list[ItemInDb]:
    try: 
        cursor = db.con.cursor()
        items = db.get_user_items(cursor,id)
        cursor.close()
    except:
        raise HTTPException(status_code=404, detail="User not found")
    if id != current_user.id:
        for item in items:
            item.description = "REDACTED"
    return items

@app.get("/items/{item_id}")
def get_item_info(item_id: int,current_user: Annotated[User, Depends(get_current_user)]) -> ItemInDb:
    try: 
        cursor = db.con.cursor()
        item = db.get_item(cursor,item_id)
        cursor.close()
    except:
        raise HTTPException(status_code=404, detail="Item or User not found")
    if item.owner != current_user.id:
        item.description = "REDACTED"
    return item

@app.post("/users/me/items")
def create_item(item: ItemInput,current_user: Annotated[User, Depends(get_current_user)]) -> ItemInDb:
    if item.price<0:
        raise HTTPException(status_code=400, detail="nonono price >0")
    cursor = db.con.cursor()
    ret_item = db.create_item(cursor, owner=current_user.id, price=item.price, name=item.name, description=item.description)
    cursor.close()
    return ret_item

@app.patch("/users/{seller_id}/items/{item_id}")
def buy_item(seller_id: int, item_id: int, price: int, current_user: Annotated[User, Depends(get_current_user)]) -> ItemInDb| None:
    cursor = db.con.cursor()
    item = db.get_item(cursor, item_id)

    if current_user.balance>=price:
        db.transfer_item(cursor, seller_id, current_user.id, item_id, price)
        cursor.close()
        return item
    
    cursor.close()
    raise HTTPException(status_code=400, detail="Balance < price")
