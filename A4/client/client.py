import socket
import sys, os

command = sys.argv[1]
filename = sys.argv[2]
hostnamePort = sys.argv[3]
hostname = hostnamePort.split(":", 1)[0]
port = int(hostnamePort.split(":", 2)[1])
cipher = sys.argv[4]
key = sys.argv[5]

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((hostname, port))

# uploading
# read from standard input and send to the server
if command == "write":
    f = open(filename, "rb")
    # tell server command
    clientSocket.send(bytearray(command, "UTF-8"))
    print("Wanting to upload", filename, "to server")

    # basically a nop, sorry
    a = clientSocket.recv(1024)

    # send name of file
    clientSocket.send(bytearray(filename, "UTF-8"))
    # send contents of file
    line = f.read(1024)
    while line:
        clientSocket.send(line)
        print("Sent and uploaded", repr(line))
        line = f.read(1024)
    print("Uploaded successfully. Good bye")
    f.close()
    clientSocket.close()

# downloading
# ask server to send contents of a file called filename
# write results to standard output
# may have to use two recv loops, one to determine size...
elif command == "read":
    # tell server command
    clientSocket.send(bytearray(command, "UTF-8"))
    print("Wanting to download", filename, "from server")

    # basically a nop sorry
    a = clientSocket.recv(1024)

    # tell server what file to download
    clientSocket.send(bytearray(filename, "UTF-8"))
    with open(filename, "wb") as f:
        print("Opened file")
        data = clientSocket.recv(1024)
        while data:
            print("receiving and writing data", repr(data))
            f.write(data)
            data = clientSocket.recv(1024)
    print("Received successfully. Good bye")
    f.close()                       # close file
    clientSocket.close()            # close connection

else:
    print("bad command \"", command, "\"")
    clientSocket.close()
