import socket
import sys, os
import cryptography
import time
import hashlib

def getTime():
    # get time
    dt = time.localtime()
    hr = str("%02d" % dt[3])
    mn = str("%02d" % dt[4])
    sc = str("%02d" % dt[5])
    return hr+":"+mn+":"+sc+": "

#####

try:
    port = int(sys.argv[1])
    key = sys.argv[2]
except:
    print("must both state port and key")
    print("exiting...")
    sys.exit()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("localhost", port))

serverSocket.listen(0)
print("Listening on port", port)
print("Using secret key:", key)



while True:
    connection, addr = serverSocket.accept()

    ip = addr[0]

    # first message
    message = connection.recv(1024)
    message = message.decode("utf-8")
    cipher = message.split(";", 1)[0]
    nonce = message.split(";", 2)[1]
    connection.send(bytearray("OK", "UTF-8"))

    # authentication
    # send challenge

    # send requests
    requests = connection.recv(1024)
    requests = requests.decode("utf-8")
    command = requests.split(";", 1)[0]
    filename = requests.split(";", 2)[1]

    IV = hashlib.sha256((key+nonce+"IV").encode("utf-8")).hexdigest()
    SK = hashlib.sha256((key+nonce+"SK").encode("utf-8")).hexdigest()

    # logging
    print(getTime()+"New connection from "+str(ip)+" cipher="+cipher)
    print(getTime()+"nonce="+str(nonce))
    print(getTime()+"IV="+str(IV))
    print(getTime()+"SK="+str(SK))
    print(getTime()+"command:"+command+", filename:"+filename)

    connection.send(bytearray("OK", "UTF-8"))

    ####                          ####
    # client to download from server #
    ####                          ####
    if command == "read":
        try:
            with open(filename, "rb") as f:
                connection.send(bytearray("OK", "utf-8"))
                connection.recv(1024)
                line = f.read(1024)
                while line:
                    print(getTime()+"sending:", repr(line))
                    connection.send(line)
                    line = f.read(1024)
                print(getTime()+"status: success")
            f.close()
        except FileNotFoundError:
            connection.send(bytearray("error - file not found", "utf-8"))
            print(getTime()+"status: error - file not found")


    ####                      ####
    # client to upload to server #
    ####                      ####
    elif command == "write":
        try:
            # check if client is able to upload
            response = (connection.recv(1024)).decode("utf-8")
            if response != "OK":
                print(getTime()+"status: error - "+response)
                continue
            else:
                print(getTime()+"status: client said "+response)
                connection.send(bytearray("OK", "utf-8"))
            with open(filename, "wb") as f:
                data = connection.recv(1024)
                while data:
                    f.write(data)
                    data = connection.recv(1024)
            f.close()
            print(getTime()+"status: success")
        except FileNotFoundError:
            print(getTime()+"status: error - file not found")
            connection.send(bytearray("error - file not found", "utf-8"))

    # not correct command (this should never be reached, actually)
    else:
        print(getTime()+"bad command \"", command, "\"")
    connection.close()
