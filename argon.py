from argon2 import PasswordHasher
import pymongo

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

user_name = input("Enter username: ")
password = input("Enter password: ")

# dict = {}
# dict['username'] = user_name
# dict['password'] = ph.hash(password)
#
client = pymongo.MongoClient("localhost:27017")
db =client['LMS']
collection = db['users']

if collection.find_one({'username':user_name}):
    user = collection.find_one({'username':user_name})['password']
    if ph.verify(user,password):
        print("Login successful")
    else:
        print("Incorrect password")



