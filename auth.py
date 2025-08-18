import pymongo as mongo
import bcrypt as en

client = mongo.MongoClient("localhost:27017")
db =client['LMS']
collection = db['users']

dict = {}

user_name = input("Enter username: ")
password = input("Enter password: ")

if collection.find_one({'username':user_name}):
    user = collection.find_one({'username':user_name})['password']
    if en.checkpw(password.encode('utf-8'), user):
        print("Login successful")
    else:
        print("Incorrect password")

