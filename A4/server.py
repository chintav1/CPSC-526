import socket
import sys, os
import cryptography
import time
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def decrypt(line, SK, IV, cipherLength):
    cipher = Cipher(algorithms.AES(SK), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()

    line = decryptor.update(line) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    line = unpadder.update(line) + unpadder.finalize()

    return line

def encrypt(line, SK, IV, cipherLength):
    cipher = Cipher(algorithms.AES(SK), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    pad = padder.update(line) + padder.finalize()

    line = encryptor.update(pad) + encryptor.finalize()

    return line


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
    cipherType = message.split(";", 1)[0]
    nonce = message.split(";", 2)[1]
    connection.send(bytearray("OK", "UTF-8"))


    # get requests
    requests = connection.recv(1024)
    requests = requests.decode("utf-8")
    command = requests.split(";", 1)[0]
    filename = requests.split(";", 2)[1]

    cipherLength = 0
    if cipherType == "aes128":
        cipherLength = 16
    elif cipherType == "aes256":
        cipherLength = 32

    salt = bytearray(nonce, "utf-8")
    # TODO: Make the length parsed from command line
    kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=16, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
    IV = kdf.derive(bytes(key+nonce+"IV", "UTF-8"))
    kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=cipherLength, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
    SK = kdf.derive(bytes(key+nonce+"SK", "UTF-8"))

    # logging
    print(getTime()+"New connection from "+str(ip)+" cipher="+cipherType)
    print(getTime()+"nonce="+str(nonce))
    print(getTime()+"IV="+str(IV))
    print(getTime()+"SK="+str(SK))
    print(getTime()+"command:"+command+", filename:"+filename)

    #connection.send(bytearray("OK", "UTF-8"))
    # send challenge
    secretmsg = "there is no spoon"



    # add padding and encryption
    cipher = Cipher(algorithms.AES(SK), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    pad = padder.update(bytes(secretmsg, "utf-8")) + padder.finalize()

    ciphertext = encryptor.update(pad) + encryptor.finalize()

    #ciphertext = encryptor.update(bytes(secretmsg, "utf-8")) + encryptor.finalize()
    connection.send(ciphertext)

    # receive response from client
    try:
        answer = (connection.recv(1024)).decode("utf-8")

        # check answer
        if answer == secretmsg:                       #right key
            print(getTime() + "Key is OK")
            connection.send(bytearray("OK", "utf-8"))

    except:
        print(getTime() + "Client used the wrong key")              #wrong key
        connection.send(bytearray("Wrong secret", "utf-8"))
        continue







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
                    line = encrypt(line, SK, IV, cipherLength)
                    print(getTime()+"sending:", repr(line))
                    connection.send(line)
                    line = f.read(1024)
            f.close()
            connection.send(encrypt(bytes("NO BYTES -- END OF FILE OK", "utf-8"), SK, IV, cipherLength))
            response = (connection.recv(1024)).decode("utf-8")
            if response != "OK":
                print(getTime()+"status: error - something went wrong")
            else:
                print(getTime()+"status: success")
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
                connection.send(bytearray("OK, please send file", "utf-8"))
            with open(filename, "wb") as f:
                data = connection.recv(1024)
                while data:
                    print("receiving and downloading data", data)
                    data = decrypt(data, SK, IV, cipherLength)
                    if (data).decode("utf-8") == "NO BYTES -- END OF FILE OK":
                        break
                    f.write(data)
                    data = connection.recv(1024)
            f.close()
            connection.send(bytearray("OK", "utf-8"))
            response = (connection.recv(1024)).decode("utf-8")
            if response != "OK":
                print(getTime()+"status: error - unable to complete uploading")
            else:
                print(getTime()+"status: success")
        except FileNotFoundError:
            print(getTime()+"status: error - file not found")
            connection.send(bytearray("error - file not found", "utf-8"))


    # not correct command (this should never be reached, actually)
    else:
        print(getTime()+"bad command \"", command, "\"")
    connection.close()
