from app.models import User, ItemInDb
import sqlite3
con = sqlite3.connect("cats.db",check_same_thread=False)

def get_users(cursor):
    return [User(id=id,balance=balance,username=username) for id,balance,username in cursor.execute("SELECT id,balance,username FROM Users", ()).fetchall()]

def get_last_users(cursor):
    return [User(id=id,balance=balance,username=username) for id,balance,username in cursor.execute("SELECT id,balance,username FROM Users ORDER BY id DESC LIMIT 20", ()).fetchall()]

def create_user(cursor,username,password):
    id, = cursor.execute("INSERT INTO Users (username,balance,password)  VALUES (?,?,?) RETURNING id;", (username,500,password)).fetchone()
    con.commit()
    return User(username=username, balance=500,id=id)

def get_user_by_username(cursor,username:str):
    id, balance = cursor.execute("SELECT id,balance FROM Users WHERE username = ? ", (username,)).fetchone()
    return User(username=username, balance=balance,id=id)

def get_user_by_id(cursor, id:int):
    username, balance = cursor.execute("SELECT username,balance FROM Users WHERE id = ? ", (id,)).fetchone()
    return User(username=username, balance=balance,id=id)

def check_password(cursor,username,password):
    real_password, = cursor.execute("SELECT password FROM Users WHERE username= ? ", (username,)).fetchone()
    return real_password==password

def get_item(cursor,item_id):
    owner,price,name,description = cursor.execute("SELECT owner,price,name,description from Items where item_id =?",(item_id,)).fetchone()
    return ItemInDb(owner=owner,price=price,name=name,description=description,item_id=item_id)

def get_user_items(cursor,owner):
    return [ItemInDb(name=name,price=price,item_id=item_id,owner=owner,description=description) for name,price,item_id,description in cursor.execute("SELECT name,price,item_id,description FROM Items WHERE owner=?", (owner,)).fetchall()]

def create_item(cursor,owner,price,name,description):
    item_id, = cursor.execute('INSERT INTO Items(owner,price,name,description) VALUES (?,?,?,?) RETURNING item_id',(owner,price,name,description)).fetchone()
    con.commit()
    return ItemInDb(owner=owner,price=price,name=name,item_id=item_id,description=description)

def transfer_item(cursor,from_,to,item_id,price):
    cursor.execute('INSERT INTO Items(owner,price,name,description) SELECT ?,price,name,description FROM Items WHERE item_id = ?',(to,item_id))
    cursor.execute('UPDATE Users SET balance =balance-? WHERE id = ?', (price, to))
    cursor.execute('UPDATE Users SET balance =balance+? WHERE id = ?', (price, from_))
    con.commit()
