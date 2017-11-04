import socket
import sys, os
import cryptography

port = int(sys.argv[1])
key = sys.argv[2]

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("localhost", port))

serverSocket.listen(0)

while True:
    connection, addr = serverSocket.accept()
    print("Connection from ", addr)

    data = connection.recv(1024)
    command = data.decode("utf-8")
    connection.send(bytearray("OK", "UTF-8"))

    # client to download from server
    if command == "read":
        data = connection.recv(1024)
        filename = data.decode("utf-8")
        print("received request to download", filename)

        try:
            f = open(filename, "rb")
            line = f.read(1024)
            print("shall send", repr(line))
            while line:
                connection.send(line)
                print("Sent ", repr(line))
                line = f.read(1024)
            f.close()
            print("Done sending")
        except Exception:
            print("An error has occured.")
            print(Exception)

    # client to upload to server
    elif command == "write":
        data = connection.recv(1024)
        filename = data.decode("utf-8")
        print("received request to upload", filename)

        # write the file to be uploaded
        with open(filename, "wb") as f:
            print("Opened file")
            data = connection.recv(1024)
            while data:
                print("receiving and writing data", repr(data))
                f.write(data)
                data = connection.recv(1024)
        print("Done receiving")
        f.close()                       # close file

    # not correct command (this should never be reached, actually)
    else:
        print("bad command \"", command, "\"")
    connection.close()
