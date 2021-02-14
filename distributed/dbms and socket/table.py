import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread

mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
mycursor = mydb.cursor()

# mycursor.execute("Create table fileBackupData(file varchar(200), owner varchar(200), port varchar(200) )")

# mycursor.execute("Show tables")
# for tb in mycursor :
#     print(tb)

files = []

userData=[]
portData =[]
files=os.listdir('backup')
# print(files)

for file in (files):
    userData.append("kartik")
    portData.append("parrot")
    
    
    
# files = tuple(zip(files, userData,portData))


# files =[]
# files.append(tuple(zip(str("file1"),str("owner1"),str("port1"))))
# files.append(tuple(zip(str("file2"),str("owner2"),str("port2"))))
# files.append(tuple(zip(str("file3"),str("owner3"),str("port3"))))
# files.append(tuple(zip(str("file4"),str("owner4"),str("port4"))))

# dataPush = "Insert into filebackupdata(file, owner, port) values (%s, %s, %s)"
# for file in files : 
#     if file not in myFiles :
#         mycursor.execute(dataPush,file)
#         mydb.commit()
# mycursor.executemany(dataPush,files)
# mydb.commit()

deleteOperation = "DELETE FROM filebackupdata"
mycursor.execute(deleteOperation)
mydb.commit()

mycursor.execute("Select * from filebackupdata")
myFiles = mycursor.fetchall()

for row in myFiles:
    print (row)