import requests
from enum import Enum

class LoginState(Enum):
    LOGGED_IN = 0
    LOGGED_OUT = 1

class UserAction(Enum):
    LIST_USERS = 1
    GET_USERINFO = 2
    GET_CURRENT_USER_INFO = 3
    CREATE_PRANK = 4
    BUY_PRANK = 5
    LOGOUT = 6

# HOST = 'http://127.0.0.1:8000'
HOST = input('enter server url')

print('''
___________.____                   __________                       __              ____  __.      __               _________.__    _______          
\_   _____/|    |    ____ ___  ___ \______   \____________    ____ |  | __         |    |/ _|____ |  | __          /   _____/|  |__ \   _  \ ______  
 |    __)  |    |  _/ __ \\  \/  /  |     ___/\_  __ \__  \  /    \|  |/ /  ______ |      <_/ __ \|  |/ /  ______  \_____  \ |  |  \/  /_\  \\____ \ 
 |     \   |    |__\  ___/ >    <   |    |     |  | \// __ \|   |  \    <  /_____/ |    |  \  ___/|    <  /_____/  /        \|   Y  \  \_/   \  |_> >
 \___  /   |_______ \___  >__/\_ \  |____|     |__|  (____  /___|  /__|_ \         |____|__ \___  >__|_ \         /_______  /|___|  /\_____  /   __/ 
     \/            \/   \/      \/                        \/     \/     \/                 \/   \/     \/                 \/      \/       \/|__|    
''')


login_state = LoginState.LOGGED_OUT
headers = {}
while True:
    if login_state==LoginState.LOGGED_OUT:
        print('''Here is your Flex SHop menu, my Homie$$$\n1) register\n2) login''')
        command = int(input("> "))
        if command == 1: #register
            username = input("Enter username: ")
            password = input("Enter password: ")
            response = requests.post(HOST+"/users/register",params={"username":username,"password":password})
            if response.status_code!=200:
                print("ERROR:",response.json()['detail'])
            else:
                print("User registred successfully!")
        elif command == 2:
            username = input("Enter username: ")
            password = input("Enter password: ")
            response = requests.post(HOST+'/token',data={"username":username,"password":password})
            if response.status_code!=200:
                print("ERROR:",response.json()['detail'])
            else:
                headers["Authorization"] = "Bearer "+response.json()['access_token']
                print("User has successfully logged in!")
                login_state = LoginState.LOGGED_IN
            
    elif login_state==LoginState.LOGGED_IN:
        print('''Now you can prank you neighbors until the die lol%%\n1)List users\n2)Get user info\n3)Get current user info and pranks\n4)Create prank&&&\n5)buy prank for your sosedi hihihaha\n6)logout''')
        command = UserAction(int(input("> ")))
        if command == UserAction.LOGOUT:
            login_state = LoginState.LOGGED_OUT
            headers = {}

        elif command==UserAction.LIST_USERS:
            response = requests.get(HOST+"/users/last/").json()
            print("Users:")
            for dct in response:
                print(str(dct['id'])+') '+dct['username'])

        elif command==UserAction.GET_CURRENT_USER_INFO:
            print("User info:")
            response = requests.get(HOST+"/users/me/",headers=headers).json()
            for k,v in response.items():
                print(k+':',v)
            print("Pranks:\n")
            response = requests.get(HOST+"/users/me/items",headers=headers).json()
            for item in response:
                print("Id:",item['item_id'])
                print("Name:", item['name'])
                print("Description:",item['description'])
                print("Price:", item['price'])
                print('----------')

        elif command==UserAction.GET_USERINFO:
            choice = int(input("1)Search by username\n2)search by id\n> "))
            if choice == 1:
                print("non implemented yet sorry")
            if choice == 2:
                id = int(input('Enter id: '))
                response = requests.get(HOST+f"/users/{id}")
                if response.status_code==200:
                    info = response.json()
                    print("User info:")
                    print("Username:", info['username'])
                    print("Balance:",info['balance'])
                    print("User items:\n")
                    response = requests.get(HOST+f"/users/{id}/items",headers=headers).json()
                    for item in response:
                        print("Id:",item['item_id'])
                        print("Name:", item['name'])
                        print("Description:",item['description'])
                        print("Price:", item['price'])
                        print('----------')
                else:
                    print("ERROR:",response.json()['detail'])

        elif command == UserAction.CREATE_PRANK:
            name = input("Enter prank name: ")
            description = input("Enter description(here is your flag btw lol): ")
            price = int(input("Enter money count for this prank: "))
            response = requests.post(HOST+'/users/me/items',json={"name":name,"price":price,"description":description},headers=headers)
            if response.status_code==200:
                print("Your prank id:",response.json()['item_id'])
            else:
                print("ERROR:",response.json()['detail'])

        elif command == UserAction.BUY_PRANK:
            prank_owner_id = int(input("Enter prank owner id: "))
            prank_id = int(input("Enter prank id: "))
            response =requests.get(HOST+f"/items/{prank_id}",headers=headers)
            if response.status_code==200:
                item = response.json()
                price = item['price']
                result = requests.patch(HOST+f"/users/{prank_owner_id}/items/{prank_id}",headers=headers,params={"price":int(price)})
                if result.status_code==200:
                    print("Prank purchased successfully ;=>$$$")
                else:
                    print("ERROR:",result.json()['detail'])
            else:
                print("ERROR:",response.json()['detail'])