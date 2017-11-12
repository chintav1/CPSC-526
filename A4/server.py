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
import struct
import binascii

# credit to: http://stupidpythonideas.blogspot.ca/2013/05/sockets-are-byte-streams-not-message.html
# for methods send_msg, recvall, and recv_msg
# and realising that padding error was due to sending files and not the actual encryption

def send_msg(s, data):
    length = len(data)
    s.send(struct.pack('!I', length))
    s.send(data)

def recvall(s, count):
    buf = b''
    while count:
        newbuf = s.recv(count)
        if not newbuf: return None
        buf = buf + newbuf
        count = count - len(newbuf)
    return buf

def recv_msg(s):
    lengthbuf = recvall(s, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(s, length)



def decrypt(line, SK, IV, cipherType):
    if cipherType == "null":
        return line

    cipher = Cipher(algorithms.AES(SK), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()

    line = decryptor.update(line) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()

    line = unpadder.update(line) + unpadder.finalize()

    return line

def encrypt(line, SK, IV, cipherType):
    if cipherType == "null":
        return line

    cipher = Cipher(algorithms.AES(SK), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    line = padder.update(line) + padder.finalize()

    line = encryptor.update(line) + encryptor.finalize()

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
serverSocket.bind(("", port))

BLOCK_SIZE = 128

serverSocket.listen(0)
print("Listening on port", port)
print("Using secret key:", key)

while True:
    connection, addr = serverSocket.accept()
    ip = addr[0]


    # first message
    # this is the only message that is not encrypted/decrypted
    message = connection.recv(BLOCK_SIZE)
    message = message.decode("utf-8")
    cipherType = message.split(";", 1)[0]
    nonce = message.split(";", 2)[1]



    '''
    try:
        answer = (connection.recv(BLOCK_SIZE))
        print("Answer = ", answer.decode("utf-8"))

        # check answer
        if ((cipherType != "null") and (answer.decode("utf-8") == secretmsg)):                       #right key
            print(getTime() + "Key is OK")
            connection.send(bytearray("OK", "utf-8"))
        else:
            print(getTime() + "null cipher is used")
            connection.send(bytearray("OK", "utf-8"))

    except:
        print(getTime() + "Client used the wrong key")              #wrong key
        #connection.send(bytearray("Wrong secret", "utf-8"))
        continue
    '''


    keyLength = 16
    if keyLength == "aes256":
        keyLength = 32

    kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=16, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
    IV = kdf.derive(bytes(key+nonce+"IV", "UTF-8"))
    kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=keyLength, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
    SK = kdf.derive(bytes(key+nonce+"SK", "UTF-8"))

    # start encryption/decryption of all messages

    # create challenge
    secretmsg = "there is no spoon"

    # send challenge
    ciphertext = encrypt(bytes(secretmsg, "utf-8"), SK, IV, cipherType)
    connection.send(ciphertext)

    # receive response from client
    # TODO: Fix this
    response = connection.recv(BLOCK_SIZE)

    if response == bytes(secretmsg, "utf-8"):
        print(getTime()+"Key OK")
    else:
        print(getTime()+"Incorrrect key")
        connection.close()
        continue

    # send response that key is good
    connection.send(encrypt(bytes("KEY OK", "utf-8"), SK, IV, cipherType))

    # logging
    print(getTime()+"New connection from "+str(ip)+" cipher="+cipherType)
    print(getTime()+"nonce="+str(nonce).upper())
    print(getTime()+"IV="+(binascii.hexlify(IV)).decode('ascii'))
    print(getTime()+"SK="+(binascii.hexlify(SK)).decode('ascii'))


    # get requests from client
    requests = decrypt(connection.recv(BLOCK_SIZE), SK, IV, cipherType)

    # print results
    requests = requests.decode("utf-8")
    command = requests.split(";", 1)[0]
    filename = requests.split(";", 2)[1]
    print(getTime()+"command:"+command+", filename:"+filename)

    # begin read or write

    ####                          ####
    # client to download from server #
    ####                          ####
    if command == "read":
        try:
            with open(filename, "rb") as f:
                # tell client if file exists
                connection.send(encrypt(bytes("OK TO READ", "utf-8"), SK, IV, cipherType))
                # get message from client if it is ready to receive
                response = decrypt(connection.recv(BLOCK_SIZE), SK, IV, cipherType)
                print(getTime()+"status: starting to send")
                if response != b"OK READY TO READ":
                    print("something went wrong")
                    continue

                # start to send file
                line = f.read(BLOCK_SIZE)
                send_msg(connection, encrypt(line, SK, IV, cipherType))
                while line:
                    #print("sending", line)
                    line = f.read(BLOCK_SIZE)
                    send_msg(connection, encrypt(line, SK, IV, cipherType))
            f.close()

            response = decrypt(connection.recv(BLOCK_SIZE), SK, IV, cipherType)
            if response == bytes("OK", "utf-8"):
                print(getTime()+"status: success")
            else:
                print(getTime()+"status: error - something went wrong")

        except FileNotFoundError:
            connection.send(encrypt(bytes("error - file not found", "utf-8"), SK, IV, cipherType))
            print(getTime()+"status: error - file not found")



    ####                      ####
    # client to upload to server #
    ####                      ####
    elif command == "write":
        try:
            # check if client is able to upload
            response = decrypt(connection.recv(BLOCK_SIZE), SK, IV, cipherType)
            if response != b"OK":
                print(getTime()+"status: error - "+response.decode("utf-8"))
                continue
            else:
                print(getTime()+"status: client said "+response.decode("utf-8"))
                connection.send(encrypt(bytes("OK", "utf-8"), SK, IV, cipherType))

            # start to receive file
            with open(filename, "wb") as f:
                print(getTime()+"status: starting to receive")
                data = recv_msg(connection)
                data = decrypt(data, SK, IV, cipherType)
                while data:
                    #print("receiving", data)
                    f.write(data)
                    data = recv_msg(connection)
                    data = decrypt(data, SK, IV, cipherType)
            f.close()

            response = decrypt(connection.recv(BLOCK_SIZE), SK, IV, cipherType)
            if response == bytes("OK", "utf-8"):
                print(getTime()+"status: success")
            else:
                print(getTime()+"status: error - something went wrong")

        except FileNotFoundError:
            print(getTime()+"status: error - file not found")
            connection.send(bytearray("error - file not found", "utf-8"))


    # not correct command (this should never be reached, actually)
    else:
        print(getTime()+"bad command \"", command, "\"")
    connection.close()
