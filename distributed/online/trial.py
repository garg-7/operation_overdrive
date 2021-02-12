import pyrebase
import os

firebaseConfig = {"apiKey": "AIzaSyCEjFB1a4S_B8immDooU32nXWyUioOC3Ww",
    "authDomain": "protocolsinarms.firebaseapp.com",
    "databaseURL": "https://protocolsinarms-default-rtdb.firebaseio.com",
    "projectId": "protocolsinarms",
    "storageBucket": "protocolsinarms.appspot.com",
    "messagingSenderId": "159255006191",
    "appId": "1:159255006191:web:df5d6ca506df02def1041a",
    "measurementId": "G-0FKTBHCNWQ"}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

userData=[]
portData =[]
portNum = 9000
files=os.listdir('backup')

for file in (files):
    portData.append(portNum)
    
files = tuple(zip(files, portData))

# data={"age":20, "address":["new york", "los angeles"]}

#push data
# for file in files :
#     db.push(file)
# db.push(data)


tasks = db.get()

for task in tasks.each() :
    print(task.val())
    
db.remove()