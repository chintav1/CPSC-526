import socket
import sys, os
import cryptography
import random
import string
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


try:
    command = sys.argv[1]
    filename = sys.argv[2]
    hostnamePort = sys.argv[3]
    hostname = hostnamePort.split(":", 1)[0]
    port = int(hostnamePort.split(":", 2)[1])
    cipherType = sys.argv[4]
    key = sys.argv[5]
except:
    print("must state command, filename, host:port, cipher, and key")
    print("exiting...")
    sys.exit()

# make sure correct cipher has been entered
if (cipherType != "null") and (cipherType != "aes128") and (cipherType != "aes256"):
    print("bad cipher \"", cipherType, "\"")
    print("exiting...")
    sys.exit()

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((hostname, port))

cipherLength = 0
if cipherType == "aes128":
    cipherLength = 16
elif cipherType == "aes256":
    cipherLength = 32

BLOCK_SIZE = 128

# used this for nonce: https://www.technologycake.com/others/generate-random-string-python/1342/
nonce = "".join(random.choice(string.ascii_letters+string.digits) for x in range(16))

IV = 0
SK = 0

if cipherType != "null":
    kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=16, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
    IV = kdf.derive(bytes(key+nonce+"IV", "UTF-8"))
    kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=cipherLength, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
    SK = kdf.derive(bytes(key+nonce+"SK", "UTF-8"))
    cipher = Cipher(algorithms.AES(SK), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()

# first message, send only cipher and nonce
clientSocket.send(bytearray(cipherType+";"+nonce, "UTF-8"))
a = clientSocket.recv(BLOCK_SIZE)

# send requests to server
clientSocket.send(bytearray(command+";"+filename, "UTF-8"))




# respond to challenge
challenge = clientSocket.recv(BLOCK_SIZE)
print("challenge")
print(challenge)


if cipherType != "null":
    answer = decrypt(challenge, SK, IV, cipherLength)
    print(answer.decode("utf-8"))
    clientSocket.send(answer)

else:
    clientSocket.send(challenge)



# get whether key is right or wrong
result = (clientSocket.recv(BLOCK_SIZE))
if result == b"OK":
    print("Key is OK")
else:
    print("Error: Wrong key")
    os._exit(1)


##         ##
# uploading #
##         ##
# read from standard input and send to the server
if command == "write":
    try:
        with open(filename, "rb") as f:
            clientSocket.send(bytearray("OK", "utf-8"))
            response = (clientSocket.recv(BLOCK_SIZE))
            print("Got the OK from server, time to upload, it said: ", response)
            line = f.read(BLOCK_SIZE)
            while line:
                if cipherType != "null":
                    line = encrypt(line, SK, IV, cipherLength)

                clientSocket.send(line)
                print("sending:", repr(line))
                line = f.read(BLOCK_SIZE)
        f.close()
        if cipherType != "null":
            clientSocket.send(encrypt(bytes("NO BYTES -- END OF FILE OK", "utf-8"), SK, IV, cipherLength))
        else:
            clientSocket.send(bytearray("NO BYTES -- END OF FILE OK", "utf-8"))
        print("finished uploading")
        response = (clientSocket.recv(BLOCK_SIZE))
        print(response.decode("utf-8"))
        if response == b"OK":
            print("OK GOOD")
        else:
            print("Please respond")
        clientSocket.send(bytearray("OK", "utf-8"))
    except FileNotFoundError:
        clientSocket.send(bytearray("file not found", "utf-8"))
        print("Error, file \"" + filename + "\" not found")
    clientSocket.close()

##           ##
# downloading #
##           ##
# ask server to send contents of a file called filename
# write results to standard output
elif command == "read":
    try:
        # check if server allows downloading
        response = (clientSocket.recv(BLOCK_SIZE))
        if b"error" in response:
            print(response)
            clientSocket.close()
            sys.exit()
        elif response == b"OK":
            print("server said " + response.decode("utf-8") + ". Starting to download")
            clientSocket.send(bytearray("OK", "utf-8"))
        else:
            print("error")
            clientSocket.close()
            sys.exit()
        with open(filename, "wb") as f:
            data = clientSocket.recv(BLOCK_SIZE)
            while data:
                #print("receiving and downloading data", data)
                if cipherType != "null":
                    data = decrypt(data, SK, IV, cipherLength)
                print(data)
                if (data == b"NO BYTES -- END OF FILE OK"):
                    break
                f.write(data)
                data = clientSocket.recv(BLOCK_SIZE)
        f.close()
        print("finished downloading")
        clientSocket.send(bytearray("OK", "utf-8"))
    except FileNotFoundError:
        print("Error, file \"" + filename + "\" not found")
    clientSocket.close()            # close connection

else:
    print("bad command \"", command, "\"")
    clientSocket.close()
