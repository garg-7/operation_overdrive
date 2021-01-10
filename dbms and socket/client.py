import mysql.connector
import os
import getpass
import socket



currentUserName = getpass.getuser()
print(currentUserName)
userData=[]

files=os.listdir('backup')
# print(files)

for file in (files):
    userData.append(currentUserName)
    
files = tuple(zip(files, userData)) 
# print(files)


# s = socket.socket()
# host = input("Please enter the hostname of the server : ")
# port = 9077
# s.connect((host, port))

# print("Enter the password to authenticate the connection ! ")
# passwordCheck = input()

# s.send(passwordCheck.encode())
# passwordVerified = s.recv(100).decode()

# if(passwordVerified == "Correct") : 
#     print("Password authentication successful")
# else : 
#     print("Password authentication unsuccessful")
#     print("The connection will be aborted")
#     exit()
    
# print("Enter Y if you want to receive a file or N if you want to participate in the file transfers")
# purpose = input()
# s.send(purpose.encode())




mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
mycursor = mydb.cursor()

# Your Computer Name is:LAPTOP-RBAGRA85
# Your Computer IP Address is:192.168.56.1

# mycursor.execute("Create database fileInfo")

# mycursor.execute("Show databases")
# for db in mycursor:
#     print (db)

# mycursor.execute("Create table backupData(file varchar(200), owner varchar(200))")

# mycursor.execute("Show tables")
# for tb in mycursor :
    # print(tb)

dataPush = "Insert into backupdata(file, owner) values (%s, %s)"

mycursor.executemany(dataPush,files)
mydb.commit()

mycursor.execute("Select * from backupdata")
myFiles = mycursor.fetchall()

for row in myFiles:
    print (row)


print(mydb)

# import socket    
# hostname = socket.gethostname()    
# IPAddr = socket.gethostbyname(hostname)    
# print("Your Computer Name is:" + hostname)    
# print("Your Computer IP Address is:" + IPAddr)    