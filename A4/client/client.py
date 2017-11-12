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
import struct

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


BLOCK_SIZE = 128

# used this for nonce: https://www.technologycake.com/others/generate-random-string-python/1342/
nonce = "".join(random.choice(string.ascii_letters+string.digits) for x in range(16))

keyLength = 16
if keyLength == "aes256":
    keyLength = 32

kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=16, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
IV = kdf.derive(bytes(key+nonce+"IV", "UTF-8"))
kdf = PBKDF2HMAC (algorithm=hashes.SHA256(), length=keyLength, salt=(bytes(nonce, "utf-8")), iterations=100000, backend=default_backend())
SK = kdf.derive(bytes(key+nonce+"SK", "UTF-8"))


# first message, send only cipher and nonce
# this is the only message that is not encrypted/decrypted
clientSocket.send(bytearray(cipherType+";"+nonce, "UTF-8"))

# start encryption/decryption all messages

# receive challenge
challenge = clientSocket.recv(BLOCK_SIZE)

# create and send answer
try:
    answer = decrypt(challenge, SK, IV, cipherType)
    #print("Answer = ", answer.decode("utf-8"))
    clientSocket.send(answer)


# get response if key is right

    result = decrypt(clientSocket.recv(BLOCK_SIZE), SK, IV, cipherType)


    if result == b"KEY OK":
        print("", end="", file=sys.stderr)
    else:
        print("Error: wrong key", file=sys.stderr)
        sys.exit()
except:
    print("Error: wrong key", file=sys.stderr)
    sys.exit()

# send requests to server
clientSocket.send(encrypt(bytes(command+";"+filename, "UTF-8"), SK, IV, cipherType))

# begin read or write

##           ##
# downloading #
##           ##
# ask server to send contents of a file called filename
# write results to standard output
if command == "read":
    try:
        # check if server allows downloading
        response = decrypt(clientSocket.recv(BLOCK_SIZE), SK, IV, cipherType)
        if b"error - file not found" in response:
            print("Error: file could not be read by server", file=sys.stderr)
            clientSocket.close()
            sys.exit()
        elif response == b"OK TO READ":
            # tell server it is ready to receive
            clientSocket.send(encrypt(bytes("OK READY TO READ", "utf-8"), SK, IV, cipherType))
        else:
            # shouldn't ever reach this
            print("error", file=sys.stderr)
            clientSocket.close()
            sys.exit()

        # begin downloading
        with open(filename, "wb") as f:
            #print("starting to receive")
            data = recv_msg(clientSocket)
            data = decrypt(data, SK, IV, cipherType)
            while data != b'':
                #print("receiving", data)
                sys.stdout.buffer.write(data)
                data = recv_msg(clientSocket)
                data = decrypt(data, SK, IV, cipherType)
        f.close()
        print("OK", file=sys.stderr)
        clientSocket.send(encrypt(bytes("OK", "utf-8"), SK, IV, cipherType))

    except FileNotFoundError:
        print("Error: file \"" + filename + "\" not found", file=sys.stderr)
    clientSocket.close()            # close connection


##         ##
# uploading #
##         ##
# read from standard input and send to the server
elif command == "write":
    try:
        with open(filename, "rb") as f:
            # tell server is is able to send
            clientSocket.send(encrypt(bytes("OK", "utf-8"), SK, IV, cipherType))
            # get response that server is ready to receive
            response = decrypt(clientSocket.recv(BLOCK_SIZE), SK, IV, cipherType)
            if response != b'OK':
                print("Error: file could not be written by server", file=sys.stderr)
                clientSocket.close()
                sys.exit()

            # begin uploading
            line = sys.stdin.buffer.read(BLOCK_SIZE)
            send_msg(clientSocket, encrypt(line, SK, IV, cipherType))
            while line:
                #print("sending", line)
                line = sys.stdin.buffer.read(BLOCK_SIZE)
                send_msg(clientSocket, encrypt(line, SK, IV, cipherType))
        f.close()
        print("OK", file=sys.stderr)
        clientSocket.send(encrypt(bytes("OK", "utf-8"), SK, IV, cipherType))

    except FileNotFoundError:
        clientSocket.send(encrypt(bytes("file not found", "utf-8"), SK, IV, cipherType))
        print("Error: file \"" + filename + "\" not found", file=sys.stderr)
    clientSocket.close()

else:
    print("Error: bad command \"", command, "\"", file=sys.stderr)
    clientSocket.close()
